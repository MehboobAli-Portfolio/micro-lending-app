from datetime import datetime, timedelta
import uuid

#payment link factory class to create payment links for invoices
class PaymentLinkFactory:
    @staticmethod
    def create_standard_link(invoice_id, base_url, days_valid=7):
        token = str(uuid.uuid4())
        expires_at = (datetime.utcnow() + timedelta(days=days_valid)).isoformat()
        payment_url = f"{base_url.rstrip('/')}/{token}"
        return {
            "invoice_id": invoice_id,
            "token": token,
            "expires_at": expires_at,
            "status": "ACTIVE",
            "payment_url": payment_url,
        }