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
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
                print(f"Error cerrando el cursor: {e}")
        try: 
            if self.connection:
                self.connection.close()
                print("Conexión cerrada")
        except Exception as e:
            print(f"Error cerrando la conexión: {e}")


    def obtener_mesas(self):
        query = """
            SELECT id, sillas, estado, pos_x, pos_y, ancho, alto, forma
            FROM mesas
        """
        return self.obtener_datos(query)
    def obtener_mesa_por_id(self, mesa_id):
        query = """
            SELECT id, sillas, estado, pos_x, pos_y, ancho, alto, forma
            FROM mesas
            WHERE id = %s
        """
        resultad = self.obtener_datos(query, (mesa_id,))
        return resultad[0] if resultad else None


# Probar conexión
if __name__ == "__main__":
    db = Database()
