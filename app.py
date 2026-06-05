from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# Habilitar CORS es vital para que el frontend en Vercel pueda comunicarse con este backend [cite: 22]
CORS(app)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Tabla usuarios [cite: 16]
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        password TEXT,
                        nombre TEXT)''')
                        
    # Tabla productos [cite: 18]
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo TEXT UNIQUE,
                        nombre TEXT,
                        descripcion TEXT,
                        precio REAL,
                        stock INTEGER,
                        categoria TEXT)''')
                        
    # Datos semilla
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (username, password, nombre) VALUES ('admin', '1234', 'administrador')")
        cursor.execute("INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria) VALUES ('P001', 'Laptop Pro', 'Laptop 16GB RAM', 3500.0, 10, 'Electrónica')")
        cursor.execute("INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria) VALUES ('P002', 'Monitor 4K', 'Monitor IPS 27 pulgadas', 1200.0, 5, 'Electrónica')")
        conn.commit()
        
    conn.close()

init_db()

# Endpoint para procesar el formulario de acceso 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuarios WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({"status": "success", "nombre": user[0]})
    return jsonify({"status": "error", "message": "Credenciales incorrectas"}), 401

# Endpoint API JSON: retorna datos del producto buscado 
@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    data = request.get_json()
    codigo = data.get('codigo')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE codigo=?", (codigo,))
    prod = cursor.fetchone()
    conn.close()
    
    if prod:
        producto_data = {
            "codigo": prod[1], "nombre": prod[2], "descripcion": prod[3], 
            "precio": prod[4], "stock": prod[5], "categoria": prod[6]
        }
        return jsonify({"status": "success", "producto": producto_data})
    
    return jsonify({"status": "error", "message": "Producto no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)