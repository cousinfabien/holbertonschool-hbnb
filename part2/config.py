# lee las variables de entorno del sistema (como las que defines en el archivo .env).
import os
# python-dotenv: permite leer archivos .env — sin ella, Python no sabría que ese archivo existe.
from dotenv import load_dotenv
# load_dotenv(): Ejecuta la carga del archivo .env. 
# Busca el archivo automáticamente en la carpeta actual y carga todas las variables que encuentre adentro. 
# A partir de esta línea, esas variables están disponibles para el sistema como si las hubieras definido manualmente.
load_dotenv()
# class Config:: Todo lo que definas aquí aplica a todos los entornos (desarrollo, producción, etc.) a menos que una subclase lo sobreescriba.
class Config:
    # Primero intenta leer la variable SECRET_KEY del sistema operativo (que load_dotenv() ya cargó desde el .env).
    # Si no la encuentra, usa 'default_secret_key' como valor de respaldo.
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    # si DEBUG estuviera en True en un servidor real, cualquier usuario podría ver los errores internos de tu aplicación.
    DEBUG = False
# Subclase que hereda todo de Config y solo cambia lo necesario para el entorno de desarrollo.
class DevelopmentConfig(Config):
    # Sobreescribe el DEBUG = False de la clase padre. Al activarlo obtenés dos beneficios durante el desarrollo:
    # El servidor se reinicia solo cada vez que guardás un archivo.
    # Si hay un error, la terminal te muestra exactamente en qué línea ocurrió.
    DEBUG = True
# Un diccionario que actúa como menú de configuraciones disponibles.
# La idea es que haga: app.config.from_object(config['development'])
# ambas claves apuntan a DevelopmentConfig
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
"""
El flujo completo cuando arrancás la app:
    1.    Python ejecuta load_dotenv() y lee el .env
    2.    os.getenv('SECRET_KEY') encuentra la clave y la asigna
    3.    Flask usa DevelopmentConfig con DEBUG = True
    4.   El servidor arranca en modo desarrollo listo para trabajar
"""
