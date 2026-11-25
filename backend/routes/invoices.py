from functools import wraps
import os
from flask import Blueprint, jsonify, request
import jwt
from database import get_db_connection
from factories.payment_link_factory import PaymentLinkFactory

invoices_bp = Blueprint("invoices", __name__)
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_micro_lending_key_2026")
BASE_PAYMENT_URL = os.getenv("BASE_PAYMENT_URL", "http://localhost:5173/pay")

#token_required decorator to protect routes, ensuring that a valid JWT token is provided in the Authorization header
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            conn = get_db_connection()
            current_user = conn.execute(
                "SELECT * FROM users WHERE id = ?", (data["user_id"],)
            ).fetchone()
            conn.close()
            if not current_user:
                raise Exception("User not found")
        except Exception:
            return jsonify({"error": "Token is invalid or expired"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

#create_invoice route to create a new invoice with customer details, protected by token authentication
@invoices_bp.route("", methods=["POST"])
@token_required
def create_invoice(current_user):
    data = request.get_json() or {}
    invoice_number = (data.get("invoice_number") or "").strip()
    customer_name = (data.get("customer_name") or "").strip()
    customer_email = (data.get("customer_email") or "").strip()
    customer_phone = (data.get("customer_phone") or "").strip()
    invoice_date = data.get("invoice_date")
    due_date = data.get("due_date")
    amount_due = data.get("amount_due")

    if (
        not invoice_number
        or not customer_name
        or not customer_email
        or not invoice_date
        or not due_date
        or amount_due is None
    ):
        return (
            jsonify(
                {
                    "error": "Customer information and mandatory invoice details are required."
                }
            ),
            400,
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            (customer_name, customer_email, customer_phone),
        )
        customer_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO invoices (invoice_number, customer_id, invoice_date, due_date, amount_due, status)
            VALUES (?, ?, ?, ?, ?, 'PENDING')
            """,
            (invoice_number, customer_id, invoice_date, due_date, amount_due),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        return jsonify({"error": "Invoice identifier already exists."}), 400

    conn.close()
    return (
        jsonify({"message": f"Invoice {invoice_number} was created successfully."}),
        201,
    )

#get_invoices route to retrieve invoices with optional search and status filters, protected by token authentication
@invoices_bp.route("", methods=["GET"])
@token_required
def get_invoices(current_user):
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    conn = get_db_connection()
    query = """
        SELECT i.id, i.invoice_number, i.invoice_date, i.due_date, i.amount_due, i.status,
               c.name as customer_name, c.email as customer_email, c.phone as customer_phone
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE 1=1
    """
    params = []

    if search_query:
        query += " AND (i.invoice_number LIKE ? OR c.name LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if status_filter:
        query += " AND i.status = ?"
        params.append(status_filter)

    query += " ORDER BY i.id DESC"
    invoices = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(row) for row in invoices]), 200

#generate_payment_link route to create a payment link for a specific invoice, protected by token authentication
@invoices_bp.route("/<int:invoice_id>/payment-link", methods=["POST"])
@token_required
def generate_payment_link(current_user, invoice_id):
    conn = get_db_connection()
    invoice = conn.execute(
        "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()

    if not invoice:
        conn.close()
        return jsonify({"error": "Invoice not found"}), 404

    if invoice["status"] == "PAID":
        conn.close()
        return jsonify({"error": "Invoice is already paid."}), 400

    link_data = PaymentLinkFactory.create_standard_link(
        invoice_id=invoice_id,
        base_url=BASE_PAYMENT_URL,
        days_valid=7,
    )

    conn.execute(
        """
        INSERT INTO payment_links (invoice_id, token, expires_at, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            link_data["invoice_id"],
            link_data["token"],
            link_data["expires_at"],
            link_data["status"],
        ),
    )
    conn.commit()
    conn.close()

    return (
        jsonify(
            {
                "payment_link": link_data["payment_url"],
                "expires_at": link_data["expires_at"],
            }
        ),
        201,
    )