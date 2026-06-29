"""
WhatsAppService – Twilio integration for bidirectional messaging.
Sends alerts to owner and customers, with graceful fallback to logging.
"""

import logging
from typing import Dict, Any, Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import Config
from app import Order  # for type hints

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Handles all WhatsApp communications via Twilio."""

    def __init__(self):
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.owner_number = Config.OWNER_WHATSAPP_NUMBER  # +923219304491
        self.twilio_configured = bool(self.account_sid and self.auth_token)
        if self.twilio_configured:
            self.client = Client(self.account_sid, self.auth_token)
            self.from_number = 'whatsapp:+14155238886'  # Twilio sandbox number
        else:
            self.client = None
            self.from_number = None
            logger.warning("Twilio credentials not set – WhatsApp messages will be logged only.")

    def _send_message(self, to_number: str, body: str) -> bool:
        """
        Internal method to send a WhatsApp message.
        Returns True if sent successfully (or logged), False on error.
        """
        if not to_number:
            logger.error("No recipient number provided.")
            return False

        # Ensure number starts with '+'
        if not to_number.startswith('+'):
            to_number = '+' + to_number

        try:
            if self.twilio_configured and self.client:
                message = self.client.messages.create(
                    body=body,
                    from_=self.from_number,
                    to=f'whatsapp:{to_number}'
                )
                logger.info(f"WhatsApp sent to {to_number}: SID {message.sid}")
                return True
            else:
                # Fallback: log the message
                logger.info(f"SIMULATED WhatsApp to {to_number}: {body}")
                return True
        except TwilioRestException as e:
            logger.error(f"Twilio error sending to {to_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp: {e}")
            return False

    def send_owner_alert(self, order_data: Dict[str, Any]) -> bool:
        """
        Send instant notification to store owner about a new order.
        order_data: dict with keys: id, customer_name, total_billing, payment_method.
        """
        order_id = order_data.get('id', 'N/A')
        customer = order_data.get('customer_name', 'Unknown')
        total = order_data.get('total_billing', 0.0)
        method = order_data.get('payment_method', 'N/A')
        msg = (
            f"🔔 NEW ORDER #{order_id}\n"
            f"Customer: {customer}\n"
            f"Total: ${total:.2f}\n"
            f"Payment: {method}\n"
            f"Action: Check admin dashboard for details."
        )
        return self._send_message(self.owner_number, msg)

    def send_customer_invoice_notification(self, customer_number: str,
                                           invoice_pdf_url: str,
                                           customer_name: str) -> bool:
        """
        Send customer a notification with invoice link.
        """
        msg = (
            f"Hi {customer_name},\n"
            f"Thank you for your order! Your invoice is ready:\n"
            f"{invoice_pdf_url}\n"
            f"Track your order status on our website."
        )
        return self._send_message(customer_number, msg)

    def send_status_update_notification(self, customer_number: str,
                                        new_status: str,
                                        tracking_id: Optional[str] = None) -> bool:
        """
        Notify customer about order status change.
        """
        if tracking_id:
            msg = f"Your order status is now: {new_status}. Tracking ID: {tracking_id}"
        else:
            msg = f"Your order status is now: {new_status}."
        return self._send_message(customer_number, msg)