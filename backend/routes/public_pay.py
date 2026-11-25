from datetime import datetime
from flask import Blueprint, jsonify
from database import get_db_connection
from observers.payment_observer import payment_events

public_pay_bp = Blueprint("public_pay", __name__)

#public route to get payment details for a given token, checking for expiration and invoice status
@public_pay_bp.route("/pay/<token>", methods=["GET"])
def get_payment_details(token):
    conn = get_db_connection()
    link = conn.execute(
        """
        SELECT pl.*, i.invoice_number, i.amount_due, i.due_date, i.status as invoice_status,
               c.name as customer_name, c.email as customer_email
        FROM payment_links pl
        JOIN invoices i ON pl.invoice_id = i.id
        JOIN customers c ON i.customer_id = c.id
        WHERE pl.token = ?
        """,
        (token,),
    ).fetchone()
    conn.close()

    if not link:
        return jsonify({"error": "Invalid payment link."}), 404

    expires_at = datetime.fromisoformat(link["expires_at"])
    if (
        datetime.utcnow() > expires_at
        or link["status"] != "ACTIVE"
        or link["invoice_status"] == "PAID"
    ):
        return (
            jsonify({"error": "Payment link has expired or invoice already paid."}),
            400,
        )

    return (
        jsonify(
            {
                "invoice_number": link["invoice_number"],
                "amount_due": link["amount_due"],
                "due_date": link["due_date"],
                "customer_name": link["customer_name"],
                "customer_email": link["customer_email"],
                "status": link["invoice_status"],
            }
        ),
        200,
    )

#public route to confirm payment for a given token, updating invoice and payment link status, and notifying observers
@public_pay_bp.route("/pay/<token>/confirm", methods=["POST"])
def confirm_payment(token):
    conn = get_db_connection()
    link = conn.execute(
        "SELECT * FROM payment_links WHERE token = ?", (token,)
    ).fetchone()

    if not link:
        conn.close()
        return jsonify({"error": "Payment link not found."}), 404

    expires_at = datetime.fromisoformat(link["expires_at"])
    if datetime.utcnow() > expires_at or link["status"] != "ACTIVE":
        conn.close()
        return jsonify({"error": "Payment link has expired."}), 400

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE invoices SET status = 'PAID' WHERE id = ?", (link["invoice_id"],)
    )
    cursor.execute(
        "UPDATE payment_links SET status = 'USED' WHERE id = ?", (link["id"],)
    )
    conn.commit()

    record = cursor.execute(
        """
        SELECT i.invoice_number, i.amount_due, c.name as customer_name, c.email as customer_email
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.id = ?
        """,
        (link["invoice_id"],),
    ).fetchone()
    conn.close()

    payload = {
        "invoice_number": record["invoice_number"],
        "amount_due": record["amount_due"],
        "customer_name": record["customer_name"],
        "customer_email": record["customer_email"],
    }
    payment_events.notify("PAYMENT_CONFIRMED", payload)

    return (
        jsonify(
            {
                "message": (
                    f"Payment of {float(record['amount_due']):.2f} for "
                    f"{record['invoice_number']} completed successfully."
                )
            }
        ),
        200,
    )