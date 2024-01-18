from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_user = 'root'
db_password = 'root'
db_host = '172.17.0.2'
db_name = 'ecommerce'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller = db.relationship('User', backref=db.backref('products', lazy=True))

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    customer = db.relationship('User', foreign_keys=[customer_id], backref=db.backref('customer_orders', lazy=True))
    seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('seller_orders', lazy=True))

class OrderProduct(db.Model):
    __tablename__ = 'orders_products'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('order_products', lazy=True))
    order = db.relationship('Order', backref=db.backref('order_products', lazy=True))

@app.route('/create_database')
def hello_world():  # put application's code here
    db.create_all()
    return 'database created'


if __name__ == '__main__':
    app.run(debug=True)
