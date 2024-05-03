from flask_sqlalchemy import SQLAlchemy
from flask import request
from config import app

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    cart = db.relationship('Cart', backref=db.backref('user', lazy=True))
    order = db.relationship('Order', backref=db.backref('user', lazy=True))
    transactions = db.relationship('Transaction', backref=db.backref('user', lazy=True))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(180), unique=False)
    product = db.relationship('Product', backref=db.backref('category', lazy=True), cascade='all, delete-orphan')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(180), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(1400), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False)
    manu_date = db.Column(db.Date, nullable=True)
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))
    
    product_image_path = db.Column(db.String(180), nullable=False)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_added_to_cart = db.Column(db.Integer, nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    #items = db.relationship('OrderItem', backref=db.backref('order', lazy=True))
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=True)
    orders = db.relationship('Order', backref=db.backref('transaction', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_time = db.Column(db.Date, nullable=False)


