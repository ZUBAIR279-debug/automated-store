"""
ShippingService – Simulates courier booking and tracking.
Integrates with TCS / Leopards API simulation.
"""

import logging
import random
import string
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.exc import SQLAlchemyError

from app import db, Order
from config import Config

logger = logging.getLogger(__name__)

class ShippingService:
    """Handles courier consignment booking and status updates."""

    def __init__(self):
        # Mock API endpoint – can be overridden from config
        self.api_endpoint = "https://api.shipping-provider.com/v1/consignments"
        self.owner_number = Config.OWNER_WHATSAPP_NUMBER  # +923219304491

    def _generate_tracking_id(self) -> str:
        """Generate a mock tracking ID (e.g., TCS123456789)."""
        prefix = random.choice(['TCS', 'LPO', 'DHL'])
        digits = ''.join(random.choices(string.digits, k=10))
        return f"{prefix}{digits}"

    def book_courier_consignment(self, order_id: int) -> Dict[str, Any]:
        """
        Book a courier for the given order.
        Returns: {'success': bool, 'tracking_id': str, 'message': str}
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {'success': False, 'error': 'Order not found'}

            # Simulate API request payload
            payload = {
                'customer_name': order.customer_name,
                'address': order.delivery_address,
                'whatsapp': order.customer_whatsapp,
                'order_id': order.id,
                'total': order.total_billing,
                'pickup_address': 'Store Warehouse, Main Blvd 123, City'  # mock
            }
            logger.info(f"Sending shipping request: {payload}")

            # === SIMULATE API CALL ===
            # In real life, you'd use requests.post() with proper auth.
            # For demo, we simulate a successful response.
            # Let's assume we get back a tracking ID.
            tracking_id = self._generate_tracking_id()
            response_status = 'success'
            response_msg = 'Consignment booked successfully.'

            if response_status == 'success':
                # Update order
                order.tracking_id = tracking_id
                order.logistics_status = 'Confirmed'
                db.session.commit()
                logger.info(f"Order {order_id} shipping confirmed. Tracking: {tracking_id}")
                return {
                    'success': True,
                    'tracking_id': tracking_id,
                    'message': 'Logistics Sync Successful: Dispatching courier rider to owner\'s production address for consignment pick-up.'
                }
            else:
                return {'success': False, 'error': 'Shipping API returned failure'}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in shipping booking: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Shipping booking error: {e}")
            return {'success': False, 'error': str(e)}

    def update_shipping_status(self, order_id: int, new_status: str) -> bool:
        """
        Manually update shipping status (e.g., 'Shipped', 'Delivered').
        Also sends notification via WhatsApp (optional).
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                logger.error(f"Order {order_id} not found for status update")
                return False
            order.logistics_status = new_status
            db.session.commit()
            logger.info(f"Order {order_id} status updated to {new_status}")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Status update error: {e}")
            return False