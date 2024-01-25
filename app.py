from flask import Flask, request, jsonify  # Asegúrate de tener esta línea
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest

app = Flask(__name__)

environment = SandboxEnvironment(client_id='Acf2jPhS1KA0Kfp9WzeeGYbQot_exWfRvQUAjhcNzygCGbsAbNCKSDDtM0z1JbYpwbllHLbdZuqe3gMX', client_secret='EDtVXB0ynpOUcUmfHbZcABOnQ_Lf8WLx-V-KE-RuVlv-Y5m6bNdHRCAZUkf1R5pzo-LrCQWN5tsVDfbz')
client = PayPalHttpClient(environment)
db_user = 'root'
db_password = 'RcBaR_-315'
db_host = '127.0.0.1'
db_name = 'db_ecommerce'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_ECHO'] = True
bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    products = db.relationship('Product', backref='seller', lazy=True, cascade="all, delete")
    customer_orders = db.relationship('Order', foreign_keys='Order.customer_id',
                                      backref='customer', lazy=True, cascade="all, delete")
    seller_orders = db.relationship('Order', foreign_keys='Order.seller_id',
                                    backref='seller', lazy=True, cascade="all, delete")
    reviews = db.relationship('Review', backref='user', lazy=True, cascade="all, delete")

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(120), nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    order_products = db.relationship('OrderProduct', backref='product', lazy=True, cascade="all, delete")
    reviews = db.relationship('Review', backref='product', lazy=True, cascade="all, delete")

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(120), nullable=False)
    order_products = db.relationship('OrderProduct', backref='order', lazy=True, cascade="all, delete")

class OrderProduct(db.Model):
    __tablename__ = 'orders_products'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Crea una nueva instancia de Product con los datos proporcionados
            new_product = Product(
                name=data['name'],
                seller_id=int(data['seller_id']),
                price=float(data['price']),
                category=data['category'],
                stock=data['stock']
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
    
@app.route('/register', methods=['POST'])    
def register():
    data = request.get_json()

    pas=bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(name=data['name'], email=data['email'], password=pas)

    db.session.add(user)
    db.session.commit()

    return 'Usuario registrado con éxito'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful!', 'user_id': user.id, 'name': user.name, 'email': user.email})
    else:
        return 'Email o contraseña incorrectos'
    
@app.route('/add_order', methods=['POST'])
def add_order():
    data = request.get_json()
    new_order = Order(
        customer_id=data['customer_id'],
        seller_id=data['seller_id'],
        amount=data['amount'],
        status=data['status']
    )
    db.session.add(new_order)
    db.session.commit()
    for product_id in data['products']:
        new_order_product = OrderProduct(
            product_id=product_id,
            order_id=new_order.id
        )
        db.session.add(new_order_product)
        db.session.commit()
    return jsonify({'message': 'Order added successfully!'})

@app.route('/products')
def products_get_all():
    productos = Product.query.all()

    lista_productos = []

    for producto in productos:
        producto_dict = {
            'id': producto.id,
            'name': producto.name,
            'price': producto.price,
            'seller': producto.seller.name,
            'category': producto.category
        }
        lista_productos.append(producto_dict)
    return jsonify(lista_productos)

@app.route('/product/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    producto = Product.query.get(producto_id)

    db.session.delete(producto)
    db.session.commit()

    # Redirige a la lista de productos o a donde desees
    return "Delete succesfully"

@app.route('/product/<string:cat>')
def products_by_category(cat):
    productos = Product.query.filter_by(category=cat)

    lista_productos = []

    for producto in productos:
        producto_dict = {
            'id': producto.id,
            'name': producto.name,
            'price': producto.price,
            'seller': producto.seller.name,
            'category':producto.category
        }
        lista_productos.append(producto_dict)
    return jsonify(lista_productos)

@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.get_json()
    new_review = Review(
        product_id=data['product_id'],
        user_id=data['user_id'],
        comment=data['comment'],
        rating=data['rating']
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'message': 'Review added successfully!'})

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    order = Order.query.get(order_id)
    order.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Order updated successfully!'})

@app.route('/orders/<int:user_id>')
def orders_get_all(user_id):
    orders = Order.query.filter_by(customer_id=user_id)
    list_orders = []
    for order in orders:
        order_dict = {
            'id': order.id,
            'customer': order.customer.name,
            'seller': order.seller.name,
            'amount': order.amount,
            'status': order.status,
            'products': [{"name": order_product.product.name, "id":order_product.product_id} for order_product in order.order_products]
        }
        list_orders.append(order_dict)
    return jsonify({"orders": list_orders})

def reviews_by_product(product_id):
    reviews = Review.query.filter_by(product_id=product_id)
    list_reviews = []
    for review in reviews:
        review_dict={
            'user_id': review.user.name,
            'comment': review.comment,
            'rating': review.rating
        }
        list_reviews.append(review_dict)
    return list_reviews

@app.route('/product_by_id/<int:id>')
def products_by_id(id):
    producto = Product.query.get(id)

    producto_dict = {
        'id': producto.id,
        'name': producto.name,
        'price': producto.price,
        'seller': producto.seller.name,
        'category':producto.category,
        'reviews':reviews_by_product(producto.id)
    }
    return jsonify(producto_dict)

@app.route('/create-paypal-order', methods=['POST'])
def create_paypal_order():
    # Obtener datos del cuerpo de la solicitud
    data = request.get_json()

    # Crear una orden en PayPal
    request = OrdersCreateRequest()
    request.prefer('return=representation')
    request.request_body(
        {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "MXN",
                        "value": data['amount']  # Monto del pago
                    }
                }
            ]
        }
    )

    try:
        # Llamar a la API de PayPal
        response = client.execute(request)
        return jsonify({'order_id': response.result.id}), 200
    except IOError as ioe:
        print(ioe)
        if isinstance(ioe, HttpError):
            print(ioe.status_code)
            print(ioe.headers)
            print(ioe)
        return jsonify({'error': 'Se produjo un error al crear la orden de PayPal'})

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True,port=5001)