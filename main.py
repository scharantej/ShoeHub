
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shoes.db'
db = SQLAlchemy(app)

Base = declarative_base()

class Shoe(Base):
    __tablename__ = 'shoes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(80), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    shoe_id = db.Column(db.Integer, db.ForeignKey('shoes.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    payment_method = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)

class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

db.create_all()

@app.route('/')
def index():
    shoes = Shoe.query.all()
    return render_template('index.html', shoes=shoes)

@app.route('/products')
def products():
    shoes = Shoe.query.all()
    return render_template('products.html', shoes=shoes)

@app.route('/product/<int:shoe_id>')
def product(shoe_id):
    shoe = Shoe.query.get_or_404(shoe_id)
    return render_template('product.html', shoe=shoe)

@app.route('/cart')
def cart():
    cart_items = CartItem.query.all()
    total_price = 0
    for item in cart_items:
        total_price += item.shoe.price * item.quantity
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    shoe_id = request.form['shoe_id']
    quantity = request.form['quantity']
    shoe = Shoe.query.get_or_404(shoe_id)
    cart_item = CartItem(shoe_id=shoe_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()
    flash('Shoe added to cart.')
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    shoe_id = request.form['shoe_id']
    quantity = request.form['quantity']
    cart_item = CartItem.query.filter_by(shoe_id=shoe_id).first()
    cart_item.quantity = quantity
    db.session.commit()
    flash('Cart updated.')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    shoe_id = request.form['shoe_id']
    cart_item = CartItem.query.filter_by(shoe_id=shoe_id).first()
    db.session.delete(cart_item)
    db.session.commit()
    flash('Shoe removed from cart.')
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    cart_items = CartItem.query.all()
    total_price = 0
    for item in cart_items:
        total_price += item.shoe.price * item.quantity
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@app.route('/place_order', methods=['POST'])
def place_order():
    user_id = request.form['user_id']
    total_price = request.form['total_price']
    shipping_address = request.form['shipping_address']
    payment_method = request.form['payment_method']
    order = Order(user_id=user_id, total_price=total_price, shipping_address=shipping_address, payment_method=payment_method, status='Processing')
    db.session.add(order)
    db.session.commit()
    flash('Order placed.')
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    name = request.form['name']
    brand = request.form['brand']
    color = request.form['color']
    size = request.form['size']
    shoes = Shoe.query
    if name:
        shoes = shoes.filter(