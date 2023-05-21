from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Dc9CeitEUe6TaleunmNP@containers-us-west-47.railway.app:5525/railway'  # Reemplaza con tus datos de conexión a la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de las extensiones
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Definición de los modelos de las tablas
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))

class Orden(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    fecha = db.Column(db.TIMESTAMP)
    total = db.Column(db.Float)
    cliente = db.relationship('Cliente', backref='ordenes')

class ProductoOrden(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    cantidad = db.Column(db.Integer)
    orden = db.relationship('Orden', backref='productos_orden')
    producto = db.relationship('Producto', backref='productos_orden')

# Definición de los esquemas de serialización con Marshmallow
class ProductoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Producto

class ClienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cliente

class OrdenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orden
    cliente = ma.Nested(ClienteSchema)

class ProductoOrdenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductoOrden
    orden = ma.Nested(OrdenSchema)
    producto = ma.Nested(ProductoSchema)

# Rutas de la API
@app.route('/productos', methods=['GET'])
def get_productos():
    productos = Producto.query.all()
    producto_schema = ProductoSchema(many=True)
    result = producto_schema.dump(productos)
    return jsonify(result)

@app.route('/clientes', methods=['GET'])
def get_clientes():
    clientes = Cliente.query.all()
    cliente_schema = ClienteSchema(many=True)
    result = cliente_schema.dump(clientes)
    return jsonify(result)

@app.route('/ordenes', methods=['GET'])
def get_ordenes():
    ordenes = Orden.query.all()
    orden_schema = OrdenSchema(many=True)
    result = orden_schema.dump(ordenes)
    return jsonify(result)

@app.route('/productos-orden', methods=['GET'])
def get_productos_orden():
    productos_orden = ProductoOrden.query.all()
    producto_orden_schema = ProductoOrdenSchema(many=True)
    result = producto_orden_schema.dump(productos_orden)
    return jsonify(result)

@app.route('/productos-orden', methods=['POST'])
def create_producto_orden():
    data = request.get_json()
    producto_id = data.get('producto_id')
    orden_id = data.get('orden_id')
    cantidad = data.get('cantidad')

    producto_orden = ProductoOrden(producto_id=producto_id, orden_id=orden_id, cantidad=cantidad)
    db.session.add(producto_orden)
    db.session.commit()

    return jsonify({'message': 'ProductoOrden creado exitosamente'}), 201

# Ejecución de la aplicación

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=os.getenv("PORT", default=5000))
