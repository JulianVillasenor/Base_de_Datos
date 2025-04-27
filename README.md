# Base_de_Datos

# Sistema de Punto de Venta con Tkinter y PostgreSQL

Este es un proyecto de implementación de una base de datos normalizada para un sistema de punto de venta. La aplicación está desarrollada en **Python**, utiliza **Tkinter** como interfaz gráfica y **PostgreSQL** como sistema gestor de base de datos. También genera facturas en PDF y gestiona inventario y ventas.

## 🎯 Objetivo

El propósito del proyecto es mostrar el uso de una base de datos relacional con entidades y sus relaciones en un entorno de aplicación real, simulando un punto de venta completo.

## 🛠️ Tecnologías utilizadas

- Python 3.12+
- Tkinter (interfaz gráfica)
- PostgreSQL (gestor de base de datos)
- psycopg2 (driver para PostgreSQL)
- reportlab (para generación de PDFs)
- Pillow (para manejo de imágenes)

## 📦 Instalación de dependencias

Antes de ejecutar el programa, asegúrate de instalar las siguientes bibliotecas:

```bash
pip install psycopg2-binary
pip install reportlab
pip install pillow
```
### Ejecucion
python index.py

### Lista de pendientes
* modelar la tabla de inventario, ventas para que cumpla con la normalizacion  
* modificar a ventas.py e inventario.py para que trabajen con las nuevas tablas normalizadas
* crear la tabla factura e implementar el uso de la tabla factura en la creacion del documento pdf que se esta haciendo obteniendo los datos de la tabla inventario y ventas
* crear la tabla proveedro, poner la llamada a el t.Frame de proveedor.py en un tk.Button dentro de inventario para poder actualizar dentro de inventario a proveedores haciendo
  la llamada del frame, proveedor y producto estan relacionados por una llave foranea
* En ventas en un tk.Button abrira al frame de facturas.py para convertir a pdf determinada factura por su folio y que no se genere al terminar la venta en automatico ya que quedaria su registro en la tabla de facturas
* Relacionar a ventas con mesa en las tablas de la base de datos y en sus clases como en el caso del Frame de ventas que pida seleccionar de que mesa o barra es el pedido
* Realizar el .txt con las querys para la creacion de la base de datos, tablas , vistas
* Implementacion del log in utilizando a la tabla usuarios como esta en el modelo de la base de datos sin implementar a el valor si es admin por el momento
* Si hay tiempo aplicar CustomTkinter para modernizar al interfaz
