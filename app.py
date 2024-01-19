from flask import Flask, request, jsonify  # Asegúrate de tener esta línea
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_user = 'userpython'
db_password = '123'
db_host = '127.0.0.1'
db_name = 'db_icomerce'

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

class review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/test')
def test():
    return 'pss'

@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        try:
            # Obtén los datos del cuerpo de la solicitud en formato JSON
            data = request.get_json()

            # Crea una nueva instancia de Product con los datos proporcionados
            new_product = Product(
                name=data['name'],
                seller_id=int(data['seller_id']),
                price=float(data['price'])
                # Puedes agregar más campos según sea necesario
            )

            # Agrega el nuevo producto a la base de datos
            db.session.add(new_product)
            db.session.commit()

            return jsonify({'message': 'Product added successfully!'}), 201  # 201 significa Created
        except KeyError as e:
            return jsonify({'error': f'Missing key: {str(e)}'}), 400  # 400 significa Bad Request
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # 500 significa Internal Server Error
    else:
        return 'Invalid request method'


@app.route('/create_database')
def create_database():  # put application's code here
    db.create_all()
    return 'Database created!'


if __name__ == '__main__':
    app.run(debug=True,port=50001)
