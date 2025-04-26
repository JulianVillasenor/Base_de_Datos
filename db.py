import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self):
        print("Iniciando conexión a la base de datos...")  # Mensaje inicial
        try:
            self.connection = psycopg2.connect(
                dbname="app_ventas",
                user="postgres",
                password="", #Poner la contraseña e informacion correcta de la base de datos para poder hace la conexion
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
            print("Conexión exitosa a PostgreSQL")
        except Exception as e:
            print(f"Error al conectar a PostgreSQL: {e}")

    def ejecutar_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f"Error ejecutando la query: {e}")

    def obtener_datos(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo datos: {e}")
            return []

    def cerrar_conexion(self):
        self.cursor.close()
        self.connection.close()

    def obtener_mesas(self):
        query = """
            SELECT id, sillas, estado, pos_x, pos_y, ancho, alto, forma
            FROM mesas
        """
        return self.obtener_datos(query)


# Probar conexión
if __name__ == "__main__":
    db = Database()
