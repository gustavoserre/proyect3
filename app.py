from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM Usuario WHERE Nombre=%s', (username,))
            user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(user['Contraseña'], password):
            session['user_id'] = user['ID_usuario']
            session['username'] = user['Nombre']
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos')
            return render_template('login.html')

    return render_template('login.html')

# Ruta de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Ruta para la página principal protegida por login
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('index.html', username=session['username'])


# -------------------------
# CRUD para la tabla Cliente
# -------------------------

# Listar clientes (con búsqueda por nombre)
@app.route('/clientes', methods=['GET', 'POST'])
def listar_clientes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search_query = request.form.get('search', '')

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        if search_query:
            cursor.execute("SELECT Nombre, Empresa, Cuit, Direccion, Telefono, Email FROM Cliente WHERE Nombre LIKE %s", ('%' + search_query + '%',))
        else:
            cursor.execute("SELECT Nombre, Empresa, Cuit, Direccion, Telefono, Email FROM Cliente")
        clientes = cursor.fetchall()
    connection.close()

    return render_template('clientes.html', clientes=clientes, search_query=search_query)

# Crear cliente
@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def crear_cliente():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        empresa = request.form['empresa']
        cuit = request.form['cuit']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO Cliente (Nombre, Empresa, Cuit, Direccion, Telefono, Email)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombre, empresa, cuit, direccion, telefono, email))
        connection.commit()
        connection.close()

        flash('Cliente creado con éxito')
        return redirect(url_for('listar_clientes'))

    return render_template('crear_cliente.html')

# Editar cliente
@app.route('/clientes/editar/<nombre>', methods=['GET', 'POST'])
def editar_cliente(nombre):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM Cliente WHERE Nombre=%s", (nombre,))
        cliente = cursor.fetchone()

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        empresa = request.form['empresa']
        cuit = request.form['cuit']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']

        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE Cliente
                SET Nombre=%s, Empresa=%s, Cuit=%s, Direccion=%s, Telefono=%s, Email=%s
                WHERE Nombre=%s
            ''', (nuevo_nombre, empresa, cuit, direccion, telefono, email, nombre))
        connection.commit()
        connection.close()

        flash('Cliente actualizado con éxito')
        return redirect(url_for('listar_clientes'))

    connection.close()
    return render_template('editar_cliente.html', cliente=cliente)

# Eliminar cliente
@app.route('/clientes/eliminar/<nombre>', methods=['POST'])
def eliminar_cliente(nombre):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM Cliente WHERE Nombre=%s", (nombre,))
    connection.commit()
    connection.close()

    flash('Cliente eliminado con éxito')
    return redirect(url_for('listar_clientes'))


# Rutas para CRUD de Producto
# ---------------------------

# Listar productos (con búsqueda por nombre)
@app.route('/productos', methods=['GET', 'POST'])
def listar_productos():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search_query = request.form.get('search', '')

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        if search_query:
            cursor.execute("SELECT Nombre, Detalle, Costo FROM Producto WHERE Nombre LIKE %s", ('%' + search_query + '%',))
        else:
            cursor.execute("SELECT Nombre, Detalle, Costo FROM Producto")
        productos = cursor.fetchall()
    connection.close()

    return render_template('productos.html', productos=productos, search_query=search_query)

# Crear producto
@app.route('/productos/nuevo', methods=['GET', 'POST'])
def crear_producto():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()

    # Obtener la lista de proveedores
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT ID_proveedor, Nombre FROM Proveedor")
        proveedores = cursor.fetchall()

    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        detalle = request.form['detalle']
        costo = request.form['costo']
        id_proveedor = request.form['id_proveedor']

        # Insertar el nuevo producto en la base de datos
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO Producto (Nombre, Detalle, Costo, ID_proveedor)
                VALUES (%s, %s, %s, %s)
            ''', (nombre, detalle, costo, id_proveedor))
        connection.commit()
        connection.close()

        # Redirigir a la lista de productos y mostrar un mensaje de éxito
        flash('Producto creado con éxito')
        return redirect(url_for('listar_productos'))

    connection.close()

    # Renderizar el formulario con la lista de proveedores
    return render_template('crear_producto.html', proveedores=proveedores)

# Editar producto
@app.route('/productos/editar/<nombre>', methods=['GET', 'POST'])
def editar_producto(nombre):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM Producto WHERE Nombre=%s", (nombre,))
        producto = cursor.fetchone()

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        detalle = request.form['detalle']
        costo = request.form['costo']
        id_proveedor = request.form['id_proveedor']

        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE Producto
                SET Nombre=%s, Detalle=%s, Costo=%s, ID_proveedor=%s
                WHERE Nombre=%s
            ''', (nuevo_nombre, detalle, costo, id_proveedor, nombre))
        connection.commit()
        connection.close()

        flash('Producto actualizado con éxito')
        return redirect(url_for('listar_productos'))

    connection.close()
    return render_template('editar_producto.html', producto=producto)

# Eliminar producto
@app.route('/productos/eliminar/<nombre>', methods=['POST'])
def eliminar_producto(nombre):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM Producto WHERE Nombre=%s", (nombre,))
    connection.commit()
    connection.close()

    flash('Producto eliminado con éxito')
    return redirect(url_for('listar_productos'))


# CRUD para la tabla Proveedor
# ---------------------------

# Listar proveedores (con búsqueda por nombre)
@app.route('/proveedores', methods=['GET', 'POST'])
def listar_proveedores():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search_query = request.form.get('search', '')

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        if search_query:
            cursor.execute("SELECT Nombre, Empresa, Cuit, Direccion, Telefono, Email FROM Proveedor WHERE Nombre LIKE %s", ('%' + search_query + '%',))
        else:
            cursor.execute("SELECT Nombre, Empresa, Cuit, Direccion, Telefono, Email FROM Proveedor")
        proveedores = cursor.fetchall()
    connection.close()

    return render_template('proveedores.html', proveedores=proveedores, search_query=search_query)

# Crear proveedor
@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def crear_proveedor():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        empresa = request.form['empresa']
        cuit = request.form['cuit']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO Proveedor (Nombre, Empresa, Cuit, Direccion, Telefono, Email)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombre, empresa, cuit, direccion, telefono, email))
        connection.commit()
        connection.close()

        flash('Proveedor creado con éxito')
        return redirect(url_for('listar_proveedores'))

    return render_template('crear_proveedor.html')

# Editar proveedor
@app.route('/proveedores/editar/<nombre>', methods=['GET', 'POST'])
def editar_proveedor(nombre):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM Proveedor WHERE Nombre=%s", (nombre,))
        proveedor = cursor.fetchone()

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        empresa = request.form['empresa']
        cuit = request.form['cuit']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        email = request.form['email']

        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE Proveedor
                SET Nombre=%s, Empresa=%s, Cuit=%s, Direccion=%s, Telefono=%s, Email=%s
                WHERE Nombre=%s
            ''', (nuevo_nombre, empresa, cuit, direccion, telefono, email, nombre))
        connection.commit()
        connection.close()

        flash('Proveedor actualizado con éxito')
        return redirect(url_for('listar_proveedores'))

    connection.close()
    return render_template('editar_proveedor.html', proveedor=proveedor)

# Eliminar proveedor
@app.route('/proveedores/eliminar/<nombre>', methods=['POST'])
def eliminar_proveedor(nombre):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM Proveedor WHERE Nombre=%s", (nombre,))
    connection.commit()
    connection.close()

    flash('Proveedor eliminado con éxito')
    return redirect(url_for('listar_proveedores'))


# CRUD para la tabla Compra
# -------------------------

# Listar compras
@app.route('/compras', methods=['GET'])
def listar_compras():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute('''
            SELECT c.ID_compra, p.Nombre as Producto, c.Cantidad, c.Costo, pr.Nombre as Proveedor
            FROM Compra c
            JOIN Producto p ON c.ID_producto = p.ID_producto
            JOIN Proveedor pr ON c.ID_proveedor = pr.ID_proveedor
        ''')
        compras = cursor.fetchall()
    connection.close()

    return render_template('compras.html', compras=compras)

# Crear compra
@app.route('/compras/nueva', methods=['GET', 'POST'])
def crear_compra():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()

    # Obtener la lista de productos y proveedores para el formulario
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT ID_producto, Nombre FROM Producto")
        productos = cursor.fetchall()
        cursor.execute("SELECT ID_proveedor, Nombre FROM Proveedor")
        proveedores = cursor.fetchall()

    if request.method == 'POST':
        # Obtener los datos del formulario
        id_producto = request.form['id_producto']
        cantidad = int(request.form['cantidad'])
        costo = float(request.form['costo'])
        id_proveedor = request.form['id_proveedor']

        # Registrar la compra en la tabla Compra
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO Compra (ID_producto, Cantidad, Costo, ID_proveedor)
                VALUES (%s, %s, %s, %s)
            ''', (id_producto, cantidad, costo, id_proveedor))

            # Actualizar el stock en la tabla Producto
            cursor.execute('''
                UPDATE Producto
                SET Detalle = Detalle,
                    Costo = GREATEST(Costo, %s),  -- Actualizamos solo si el costo es mayor al existente
                    Stock = Stock + %s
                WHERE ID_producto = %s
            ''', (costo, cantidad, id_producto))

        connection.commit()
        connection.close()

        flash('Compra registrada con éxito y stock actualizado')
        return redirect(url_for('listar_compras'))

    connection.close()

    return render_template('crear_compra.html', productos=productos, proveedores=proveedores)

# Editar compra (opcional)
@app.route('/compras/editar/<int:id_compra>', methods=['GET', 'POST'])
def editar_compra(id_compra):
    # Código para editar una compra
    pass

# Eliminar compra
@app.route('/compras/eliminar/<int:id_compra>', methods=['POST'])
def eliminar_compra(id_compra):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Eliminar la compra de la tabla Compra
        cursor.execute("DELETE FROM Compra WHERE ID_compra = %s", (id_compra,))
    connection.commit()
    connection.close()

    flash('Compra eliminada con éxito')
    return redirect(url_for('listar_compras'))


# CRUD para la tabla Venta
# ------------------------

# Listar ventas
@app.route('/ventas', methods=['GET'])
def listar_ventas():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute('''
            SELECT v.ID_venta, p.Nombre as Producto, c.Nombre as Cliente, v.Cantidad, v.Precio_de_venta
            FROM Venta v
            JOIN Producto p ON v.ID_producto = p.ID_producto
            JOIN Cliente c ON v.ID_cliente = c.ID_cliente
        ''')
        ventas = cursor.fetchall()
    connection.close()

    return render_template('ventas.html', ventas=ventas)

# Crear venta
@app.route('/ventas/nueva', methods=['GET', 'POST'])
def crear_venta():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()

    # Obtener la lista de productos y clientes para el formulario
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT ID_producto, Nombre FROM Producto")
        productos = cursor.fetchall()
        cursor.execute("SELECT ID_cliente, Nombre FROM Cliente")
        clientes = cursor.fetchall()

    if request.method == 'POST':
        # Obtener los datos del formulario
        id_producto = request.form['id_producto']
        cantidad = int(request.form['cantidad'])
        precio_de_venta = float(request.form['precio_de_venta'])
        id_cliente = request.form['id_cliente']

        # Registrar la venta en la tabla Venta
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO Venta (ID_cliente, ID_producto, Cantidad, Precio_de_venta)
                VALUES (%s, %s, %s, %s)
            ''', (id_cliente, id_producto, cantidad, precio_de_venta))

            # Actualizar el stock en la tabla Producto
            cursor.execute('''
                UPDATE Producto
                SET Stock = Stock - %s
                WHERE ID_producto = %s AND Stock >= %s
            ''', (cantidad, id_producto, cantidad))

            if cursor.rowcount == 0:
                connection.rollback()
                flash('No hay suficiente stock para este producto', 'danger')
                connection.close()
                return redirect(url_for('crear_venta'))

        connection.commit()
        connection.close()

        flash('Venta registrada con éxito y stock actualizado')
        return redirect(url_for('listar_ventas'))

    connection.close()

    return render_template('crear_venta.html', productos=productos, clientes=clientes)

# Editar venta (opcional)
@app.route('/ventas/editar/<int:id_venta>', methods=['GET', 'POST'])
def editar_venta(id_venta):
    # Código para editar una venta
    pass

# Eliminar venta
@app.route('/ventas/eliminar/<int:id_venta>', methods=['POST'])
def eliminar_venta(id_venta):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Eliminar la venta de la tabla Venta
        cursor.execute("DELETE FROM Venta WHERE ID_venta = %s", (id_venta,))
    connection.commit()
    connection.close()

    flash('Venta eliminada con éxito')
    return redirect(url_for('listar_ventas'))

if __name__ == '__main__':
    app.run(debug=True)



