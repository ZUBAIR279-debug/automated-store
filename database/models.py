from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    internet_fetched_cost = db.Column(db.Float, nullable=True)  # cost from external sources
    price = db.Column(db.Float, nullable=False)
    stock_count = db.Column(db.Integer, default=0)
    is_new_arrival = db.Column(db.Boolean, default=False)
    is_best_seller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_whatsapp = db.Column(db.String(50), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    total_billing = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # Card, Easypaisa, Jazzcash, COD
    payment_status = db.Column(db.String(50), default='Pending')  # Pending, Verified, Failed
    invoice_pdf_path = db.Column(db.String(500), nullable=True)
    logistics_status = db.Column(db.String(50), default='Pending')  # Pending, Confirmed, Shipped, Delivered
    tracking_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id} - {self.customer_name}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)  # price at time of order

    def __repr__(self):
        return f'<OrderItem order={self.order_id} product={self.product_id}>'