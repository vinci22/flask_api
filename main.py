from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os


# Configuración de la aplicación Flask
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Dc9CeitEUe6TaleunmNP@containers-us-west-47.railway.app:5525/railway'  # Reemplaza con tus datos de conexión a la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de las extensiones
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Definición de los modelos de las tablas

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    correo = db.Column(db.String(255))
    contraseña = db.Column(db.String(255))
        

class GrupoProducto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255))

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo_producto.id'))
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)
    imagen = db.Column(db.String(255))
    grupo = db.relationship('GrupoProducto', backref='productos')

    

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

class UsuariosSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuarios
        
class GrupoProductoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GrupoProducto

class ProductoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Producto
    grupo = ma.Nested(GrupoProductoSchema)
  

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

class UsuariosSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuarios

# Rutas de la API
@app.route('/insertarusuario', methods=['POST'])
def insertar_usuario():
    # Obtener los datos enviados en la solicitud
    datos = request.get_json()

    # Verificar que todas las claves existan en el diccionario de datos
    if 'nombre' not in datos or 'email' not in datos or 'password' not in datos:
        return jsonify({'error': 'Faltan datos requeridos'}), 400

    # Crear una nueva instancia de Usuarios con los datos recibidos
    nuevo_usuario = Usuarios(nombre=datos['nombre'], correo=datos['email'], contraseña=datos['password'])

    # Insertar el nuevo usuario en la base de datos
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Retornar una respuesta con el usuario insertado
    return jsonify({'message': 'creado exitosamente'}), 201


@app.route('/productos', methods=['GET'])
def get_productos():
    productos = Producto.query.all()
    producto_schema = ProductoSchema(many=True)
    result = producto_schema.dump(productos)
    response = jsonify(result)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/crear_productos', methods=['POST'])
def create_producto():
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    precio = data.get('precio')
    stock = data.get('stock')

    producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock)
    db.session.add(producto)
    db.session.commit()

    return jsonify({'message': 'Producto creado exitosamente'}), 201


@app.route('/producto', methods=['GET'])
def get_producto():
    data = request.get_json()
    producto_id = data.get('id')
    producto = Producto.query.get(producto_id)
    producto_schema = ProductoSchema()
    result = producto_schema.dump(producto)
    return jsonify(result)


@app.route('/productoByGroup', methods=['GET'])
def producto_By_group():
    grupo_id = request.args.get('id')
    producto = Producto.query.filter_by(grupo_id=grupo_id).all()
    producto_schema = ProductoSchema(many=True)
    result = producto_schema.dump(producto)
    response = jsonify(result)
    return response
    


@app.route('/productos/<int:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    producto = Producto.query.get(producto_id)
    data = request.get_json()
    producto.nombre = data.get('nombre')
    producto.descripcion = data.get('descripcion')
    producto.precio = data.get('precio')
    producto.stock = data.get('stock')
    db.session.commit()
    return jsonify({'message': 'Producto actualizado exitosamente'})


@app.route('/productos/<int:producto_id>', methods=['DELETE'])
def delete_producto(producto_id):
    producto = Producto.query.get(producto_id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado exitosamente'})


@app.route('/clientes', methods=['GET'])
def get_clientes():
    clientes = Cliente.query.all()
    cliente_schema = ClienteSchema(many=True)
    result = cliente_schema.dump(clientes)
    return jsonify(result)


@app.route('/crear_clientes', methods=['POST'])
def create_cliente():
    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')
    telefono = data.get('telefono')
    direccion = data.get('direccion')

    cliente = Cliente(nombre=nombre, email=email, telefono=telefono, direccion=direccion)
    db.session.add(cliente)
    db.session.commit()

    return jsonify({'message': 'Cliente creado exitosamente'}), 201


@app.route('/clientes/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    cliente_schema = ClienteSchema()
    result = cliente_schema.dump(cliente)
    return jsonify(result)


@app.route('/clientes/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    data = request.get_json()
    cliente.nombre = data.get('nombre')
    cliente.email = data.get('email')
    cliente.telefono = data.get('telefono')
    cliente.direccion = data.get('direccion')
    db.session.commit()
    return jsonify({'message': 'Cliente actualizado exitosamente'})


@app.route('/clientes/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    return jsonify({'message': 'Cliente eliminado exitosamente'})


@app.route('/ordenes', methods=['GET'])
def get_ordenes():
    ordenes = Orden.query.all()
    orden_schema = OrdenSchema(many=True)
    result = orden_schema.dump(ordenes)
    return jsonify(result)


@app.route('/crear_ordenes', methods=['POST'])
def create_orden():
    data = request.get_json()
    cliente_id = data.get('cliente_id')
    fecha = data.get('fecha')
    total = data.get('total')

    orden = Orden(cliente_id=cliente_id, fecha=fecha, total=total)
    db.session.add(orden)
    db.session.commit()

    return jsonify({'message': 'Orden creada exitosamente'}), 201


@app.route('/ordenes/<int:orden_id>', methods=['GET'])
def get_orden(orden_id):
    orden = Orden.query.get(orden_id)
    orden_schema = OrdenSchema()
    result = orden_schema.dump(orden)
    return jsonify(result)


@app.route('/ordenes/<int:orden_id>', methods=['PUT'])
def update_orden(orden_id):
    orden = Orden.query.get(orden_id)
    data = request.get_json()
    orden.cliente_id = data.get('cliente_id')
    orden.fecha = data.get('fecha')
    orden.total = data.get('total')
    db.session.commit()
    return jsonify({'message': 'Orden actualizada exitosamente'})


@app.route('/ordenes/<int:orden_id>', methods=['DELETE'])
def delete_orden(orden_id):
    orden = Orden.query.get(orden_id)
    db.session.delete(orden)
    db.session.commit()
    return jsonify({'message': 'Orden eliminada exitosamente'})


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


@app.route('/productos-orden/<int:producto_orden_id>', methods=['GET'])
def get_producto_orden(producto_orden_id):
    producto_orden = ProductoOrden.query.get(producto_orden_id)
    producto_orden_schema = ProductoOrdenSchema()
    result = producto_orden_schema.dump(producto_orden)
    return jsonify(result)


@app.route('/productos-orden/<int:producto_orden_id>', methods=['PUT'])
def update_producto_orden(producto_orden_id):
    producto_orden = ProductoOrden.query.get(producto_orden_id)
    data = request.get_json()
    producto_orden.producto_id = data.get('producto_id')
    producto_orden.orden_id = data.get('orden_id')
    producto_orden.cantidad = data.get('cantidad')
    db.session.commit()
    return jsonify({'message': 'ProductoOrden actualizado exitosamente'})


@app.route('/productos-orden/<int:producto_orden_id>', methods=['DELETE'])
def delete_producto_orden(producto_orden_id):
    producto_orden = ProductoOrden.query.get(producto_orden_id)
    db.session.delete(producto_orden)
    db.session.commit()
    return jsonify({'message': 'ProductoOrden eliminado exitosamente'})


# Ejecución de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=os.getenv("PORT", default=5000))
