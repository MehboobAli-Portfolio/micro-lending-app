from datetime import datetime

#payment observer classes to handle payment events and notify observers
class PaymentObserver:
    def update(self, event_name, payload):
        raise NotImplementedError("Subclasses must implement update()")

#class to log payment confirmations to the console
class ConsoleReceiptObserver(PaymentObserver):
    def update(self, event_name, payload):
        if event_name == "PAYMENT_CONFIRMED":
            timestamp = datetime.utcnow().isoformat()
            print(
                f"[{timestamp}] PAYMENT_CONFIRMED | Invoice: {payload['invoice_number']} | "
                f"Customer: {payload['customer_name']} ({payload['customer_email']}) | "
                f"Amount: {float(payload['amount_due']):.2f}"
            )

#class Mailer:
#    def send_receipt(self, payload):
class PaymentNotificationObserver(PaymentObserver):
    def __init__(self, mailer=None):
        self.mailer = mailer

    def update(self, event_name, payload):
        if event_name == "PAYMENT_CONFIRMED":
            if self.mailer:
                self.mailer.send_receipt(payload)
            else:
                print(
                    f"[NOTIFICATION QUEUED] Receipt prepared for {payload['customer_email']} "
                    f"regarding invoice {payload['invoice_number']}."
                )

#payment event subject class to manage observers and notify them of payment events
class PaymentEventSubject:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_name, payload):
        for observer in list(self._observers):
            observer.update(event_name, payload)


payment_events = PaymentEventSubject()
payment_events.subscribe(ConsoleReceiptObserver())
payment_events.subscribe(PaymentNotificationObserver())