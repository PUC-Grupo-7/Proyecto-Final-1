import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("instance/db.sqlite3")

# Crear un cursor y listar las tablas
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tablas en la base de datos:", tables)

conn.close()
