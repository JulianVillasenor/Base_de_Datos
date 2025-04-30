import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self):
        print("Iniciando conexión a la base de datos...")  # Mensaje inicial
        try:
            self.connection = psycopg2.connect(
                dbname="app_ventas",
                user="postgres",
                password="Matamoscas17", #Poner la contraseña e informacion correcta de la base de datos para poder hace la conexion
                host="localhost",
                port="5432"
            )
            self.cursor = self.connection.cursor()
            print("Conexión exitosa a PostgreSQL")
        except Exception as e:
            print(f"Error al conectar a PostgreSQL: {e}")

    def ejecutar_query(self, query, params=None, return_id=False):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            if return_id:
                return self.cursor.fetchone()[0]  # Retorna el ID de la última fila insertada
            else:
                return self.cursor.rowcount  # Retorna el número de filas afectadas
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
    
    def asociar_venta_a_folio(self, id_venta, folio):
        query = "INSERT  INTO factura (id_venta, folio) VALUES (%s, %s)"
        try:
            self.ejecutar_query(query, (id_venta, folio))
            self.connection.commit()
            print("Folio asociado a la venta correctamente.")
        except Exception as e:
            print(f"Error al asociar el folio a la venta: {e}")

    def obtener_venta_por_folio(self, folio):
        query = """
            SELECT id_venta, folio
            FROM factura
            WHERE folio = %s
        """
        resultado = self.obtener_datos(query, (folio,))
        return resultado[0] if resultado else None
    def ids_mesas(self):
        query = "SELECT id FROM mesas"
        self.ejecutar_query(query)
        return self.cursor.fetchall()
    #PAra la funcion pagar en ventas.py
    def obtener_id_producto(self, nombre_producto):
        query = "Select id FROM inventario WHERE nombre = %s"
        resultado = self.obtener_datos(query, (nombre_producto,))
        if resultado:
            return resultado[0][0]
        else:
            print(f"Producto '{nombre_producto}' no encontrado en la base de datos.")
            return None



# Probar conexión
if __name__ == "__main__":
    db = Database()
