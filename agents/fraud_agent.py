"""
FraudAgent – Risk evaluation and order confirmation trigger.
Validates order data and sends WhatsApp confirmation request.
"""

import logging
import re
from typing import Dict, Any, Optional

from sqlalchemy.exc import SQLAlchemyError

from app import db, Order
from config import Config

# Placeholder for Twilio client – we'll use a mock for now
try:
    from twilio.rest import Client
    twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
except:
    twilio_client = None
    logger = logging.getLogger(__name__)
    logger.warning("Twilio client not available – WhatsApp messages will be logged only.")

logger = logging.getLogger(__name__)

class FraudAgent:
    """
    Evaluates orders for fraud risk and sends confirmation messages via WhatsApp.
    """

    def __init__(self):
        self.admin_number = Config.OWNER_WHATSAPP_NUMBER  # +923219304491

    def evaluate_order_risk(self, order_id: int) -> Dict[str, Any]:
        """
        Analyze order metadata, assign risk score, and trigger confirmation.
        Returns: {'risk_score': 0-100, 'action': 'confirm', 'message': str}
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {'error': 'Order not found'}

            risk = 0
            reasons = []

            # Check address: if too short or contains suspicious patterns
            addr = order.delivery_address.lower()
            if len(addr) < 10:
                risk += 20
                reasons.append("Address too short")
            if '123 main' in addr or 'test' in addr:
                risk += 30
                reasons.append("Suspicious test address")

            # Check WhatsApp number: must be valid Pakistani format
            phone = order.customer_whatsapp
            if not re.match(r'^\+92\d{10}$', phone):
                risk += 20
                reasons.append("Invalid WhatsApp number format")

            # High-value items (total > $2000) increase risk
            if order.total_billing > 2000:
                risk += 25
                reasons.append("High-value order")

            # Payment method COD is inherently riskier
            if order.payment_method == 'COD':
                risk += 15
                reasons.append("Cash on Delivery")

            # Cap risk at 100
            risk = min(risk, 100)

            action = 'confirm' if risk < 50 else 'flag_for_review'
            if risk >= 70:
                action = 'suspend'

            # Log
            logger.info(f"Order {order_id} risk score: {risk}, action: {action}, reasons: {reasons}")

            # If action is 'confirm', send WhatsApp confirmation request to customer
            if action == 'confirm':
                self._send_confirmation_whatsapp(order)

            return {
                'risk_score': risk,
                'action': action,
                'reasons': reasons,
                'order_id': order_id
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in risk evaluation: {e}")
            return {'error': str(e)}

    def _send_confirmation_whatsapp(self, order: Order) -> bool:
        """
        Send a confirmation prompt to the customer via WhatsApp.
        For demo, we log the message. If Twilio is configured, send real message.
        """
        message = f"Thank you for your order #{order.id}. Please reply CONFIRM to proceed with delivery."
        try:
            if twilio_client:
                # Use Twilio to send WhatsApp message
                twilio_client.messages.create(
                    body=message,
                    from_='whatsapp:+14155238886',  # Twilio sandbox number
                    to=f'whatsapp:{order.customer_whatsapp}'
                )
                logger.info(f"Confirmation sent to {order.customer_whatsapp}")
            else:
                # Log only
                logger.info(f"SIMULATED WhatsApp to {order.customer_whatsapp}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp: {e}")
            return False

    def process_order(self, order_id: int) -> Dict[str, Any]:
        """
        Full pipeline: evaluate and update logistics_status if confirmed.
        """
        result = self.evaluate_order_risk(order_id)
        if 'error' in result:
            return result

        # If action is 'confirm', we could set logistics_status to 'Confirmed' automatically,
        # but we'll wait for customer response. For now, we just return.
        # In a real scenario, we'd have a webhook to handle the reply.
        return result