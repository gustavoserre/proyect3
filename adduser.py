from werkzeug.security import generate_password_hash
import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='dbproyecto3'
)

# Generar hash de contraseña
hashed_password = generate_password_hash('develop')
# usuario admin contraseña develop
with connection.cursor() as cursor:
    # Insertar un usuario
    cursor.execute('''
        INSERT INTO Usuario (Nombre, Contraseña) 
        VALUES (%s, %s)
    ''', ('admin', hashed_password))

connection.commit()
connection.close()
