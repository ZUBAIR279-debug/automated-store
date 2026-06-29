"""
InvoiceService – Generates PDF invoices using fpdf2.
Structure: Theme‑matching header, order details, itemized table, totals.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any

from fpdf import FPDF
from app import Order, OrderItem, Product

logger = logging.getLogger(__name__)

class InvoiceService:
    """Generate professional PDF invoices for orders."""

    def __init__(self):
        self.invoice_dir = os.path.join('static', 'invoices')
        # Create directory if it doesn't exist
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)
            logger.info(f"Created invoice directory: {self.invoice_dir}")

    def generate_invoice_pdf(self, order_id: int) -> str:
        """
        Generate PDF invoice for the given order ID.
        Returns the absolute file path of the generated PDF.
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError(f"Order {order_id} not found")

            # Fetch order items with product details
            items = OrderItem.query.filter_by(order_id=order.id).all()

            pdf = FPDF()
            pdf.add_page()

            # --- Header: Theme 1 (Slate + Indigo) ---
            pdf.set_fill_color(79, 70, 229)   # Indigo-600
            pdf.rect(0, 0, 210, 45, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 20, 'STORE v3', ln=True, align='C')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, 'AUTONOMOUS E-COMMERCE INVOICE', ln=True, align='C')
            pdf.set_text_color(0, 0, 0)

            # --- Order Metadata ---
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(60, 8, f'Order ID: #{order.id}', ln=0)
            pdf.cell(0, 8, f'Date: {order.created_at.strftime("%Y-%m-%d %H:%M")}', ln=1)
            pdf.set_font('Arial', '', 12)
            pdf.cell(60, 8, f'Customer: {order.customer_name}', ln=0)
            pdf.cell(0, 8, f'WhatsApp: {order.customer_whatsapp}', ln=1)
            pdf.multi_cell(0, 8, f'Address: {order.delivery_address}')
            pdf.ln(4)

            # --- Itemized Table ---
            pdf.set_font('Arial', 'B', 11)
            pdf.set_fill_color(226, 232, 240)  # slate-200
            pdf.cell(80, 10, 'Product', border=1, fill=True)
            pdf.cell(30, 10, 'Qty', border=1, fill=True, align='C')
            pdf.cell(40, 10, 'Unit Price', border=1, fill=True, align='R')
            pdf.cell(40, 10, 'Total', border=1, fill=True, align='R')
            pdf.ln()

            pdf.set_font('Arial', '', 11)
            total_sum = 0.0
            for item in items:
                product = Product.query.get(item.product_id)
                product_name = product.name if product else f"Product #{item.product_id}"
                subtotal = item.quantity * item.unit_price
                total_sum += subtotal
                pdf.cell(80, 10, product_name[:60], border=1)
                pdf.cell(30, 10, str(item.quantity), border=1, align='C')
                pdf.cell(40, 10, f"${item.unit_price:.2f}", border=1, align='R')
                pdf.cell(40, 10, f"${subtotal:.2f}", border=1, align='R')
                pdf.ln()

            # --- Totals ---
            pdf.ln(4)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(150, 10, 'Subtotal:', align='R')
            pdf.cell(0, 10, f'${total_sum:.2f}', align='R')
            pdf.ln()
            # Add delivery charge (mock)
            delivery = 29.0
            pdf.cell(150, 10, 'Delivery:', align='R')
            pdf.cell(0, 10, f'${delivery:.2f}', align='R')
            pdf.ln()
            grand_total = total_sum + delivery
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(79, 70, 229)  # Indigo
            pdf.cell(150, 12, 'GRAND TOTAL:', align='R')
            pdf.cell(0, 12, f'${grand_total:.2f}', align='R')
            pdf.set_text_color(0, 0, 0)

            # --- Footer ---
            pdf.ln(10)
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, 'Thank you for your purchase!', align='C')

            # Save PDF
            filename = f'invoice_{order.id}.pdf'
            filepath = os.path.join(self.invoice_dir, filename)
            pdf.output(filepath)
            logger.info(f"Invoice PDF generated: {filepath}")
            return os.path.abspath(filepath)

        except Exception as e:
            logger.error(f"Invoice generation failed: {e}")
            raise

    def generate_invoice_for_order_object(self, order: Order) -> str:
        """Overload to accept order object directly (convenience)."""
        return self.generate_invoice_pdf(order.id)