from datetime import datetime
from flask import Blueprint, jsonify, request
from database import get_db_connection

public_pay_bp = Blueprint('public_pay', __name__)

@public_pay_bp.route('/pay/<token>', methods=['GET'])
def get_payment_details(token):
    conn = get_db_connection()
    link = conn.execute('''
        SELECT pl.*, i.invoice_number, i.amount_due, i.due_date, i.status as invoice_status,
               c.name as customer_name, c.email as customer_email
        FROM payment_links pl
        JOIN invoices i ON pl.invoice_id = i.id
        JOIN customers c ON i.customer_id = c.id
        WHERE pl.token = ?
    ''', (token,)).fetchone()
    conn.close()
    
    if not link:
        return jsonify({'error': 'Invalid payment link.'}), 404
        
    expires_at = datetime.fromisoformat(link['expires_at'])
    if datetime.utcnow() > expires_at or link['status'] == 'EXPIRED' or link['invoice_status'] == 'PAID':
        return jsonify({'error': 'Payment link has expired or invoice already paid.'}), 400
        
    return jsonify({
        'invoice_number': link['invoice_number'],
        'amount_due': link['amount_due'],
        'due_date': link['due_date'],
        'customer_name': link['customer_name'],
        'customer_email': link['customer_email'],
        'status': link['invoice_status']
    }), 200


@public_pay_bp.route('/pay/<token>/confirm', methods=['POST'])
def confirm_payment(token):
    conn = get_db_connection()
    link = conn.execute('SELECT * FROM payment_links WHERE token = ?', (token,)).fetchone()
    
    if not link:
        conn.close()
        return jsonify({'error': 'Payment link not found.'}), 404
        
    expires_at = datetime.fromisoformat(link['expires_at'])
    if datetime.utcnow() > expires_at or link['status'] != 'ACTIVE':
        conn.close()
        return jsonify({'error': 'Payment link has expired.'}), 400
        
    cursor = conn.cursor()
    cursor.execute('UPDATE invoices SET status = "PAID" WHERE id = ?', (link['invoice_id'],))
    cursor.execute('UPDATE payment_links SET status = "USED" WHERE id = ?', (link['id'],))
    conn.commit()
    
    invoice = cursor.execute('SELECT invoice_number, amount_due FROM invoices WHERE id = ?', (link['invoice_id'],)).fetchone()
    conn.close()
    
    return jsonify({
        'message': f"Payment of ${invoice['amount_due']:.2f} for {invoice['invoice_number']} completed successfully."
    }), 200