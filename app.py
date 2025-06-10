from flask import Flask, request, jsonify
from models import db, Producto

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///almacen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    return jsonify([p.to_dict() for p in productos])

@app.route('/productos', methods=['POST'])
def agregar_producto():
    data = request.get_json()
    nombre = data.get('nombre')
    precio = data.get('precio')
    cantidad = data.get('cantidad', 0)
    if not nombre or precio is None:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    nuevo = Producto(nombre=nombre, precio=precio, cantidad=cantidad)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201

@app.route('/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    producto = Producto.query.get(id_producto)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    db.session.delete(producto)
    db.session.commit()
    return jsonify({"mensaje": f"Producto con id {id_producto} eliminado"}), 200

@app.route('/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    producto = db.session.get(Producto, id_producto) 
    if not producto:
        return jsonify({"error": "Producto no encontrado."}), 404

    data = request.get_json()

    if 'nombre' in data:
        if data['nombre'] != producto.nombre and Producto.query.filter_by(nombre=data['nombre']).first():
            return jsonify({"error": f"El nombre '{data['nombre']}' ya está en uso por otro producto."}), 409
        producto.nombre = data['nombre']
    if 'cantidad' in data:
        producto.cantidad = data['cantidad']
    if 'precio' in data:
        producto.precio = data['precio']

    db.session.commit()

    return jsonify(producto.to_dict()), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()    
    app.run(debug=True)