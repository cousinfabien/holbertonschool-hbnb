#   HBnB Part 3 — Resumen general
La Part 3 extiende la API de la Part 2 con tres mejoras principales:
1. **Autenticación y Autorización**
Se agrega un sistema de login con JWT (JSON Web Tokens).  
Cuando un usuario se loguea con email y password, recibe un token que usa para acceder a los endpoints protegidos.  
Además se implementa control de roles: 
-   Los usuarios regulares solo pueden modificar sus propios datos
-   Los administradores pueden modificar cualquier cosa.
2. **Base de datos real**
Se reemplaza el repositorio en memoria (los datos se perdían al reiniciar la app) por `SQLite` usando `SQLAlchemy` como ORM.  
`SQLAlchemy` permite trabajar con la base de datos usando Python en vez de SQL puro.  
En producción se cambia `SQLite` por `MySQL`.
3. **Diseño y visualización del esquema**
Se crean diagramas ER con `Mermaid.js` para documentar visualmente cómo se relacionan las entidades (`User`, `Place`, `Review`, `Amenity`) en la base de datos.  
También se escriben scripts SQL puros para crear las tablas e insertar datos iniciales (usuario admin y amenities básicas).


**Resumen**: la Part 2 era un prototipo funcional. La Part 3 la convierte en una aplicación real, segura y con persistencia de datos.

---
---

# Task 0 — Modify the Application Factory to Include the Configuration
## ¿Qué es el Application Factory Pattern?

El **Application Factory** es un patrón de diseño en Flask donde en vez de crear la app Flask directamente al inicio del archivo, la creás dentro de una función llamada `create_app()`. Esto te permite:

- Crear múltiples instancias de la app con distintas configuraciones (desarrollo, producción, testing)
- Evitar importaciones circulares
- Facilitar el testing

## ¿Qué había antes en `app/__init__.py`?

```python
def create_app():
    app = Flask(__name__)
    # ...
    return app
```

El problema es que `create_app()` no recibía ningún parámetro, entonces siempre usaba la misma configuración hardcodeada.  
La clase `Config` en `config.py` existía pero nunca se usaba.

## ¿Qué cambia en el Task 0?

Tres cosas:

1. `create_app()` ahora recibe un parámetro `config_class`
2. La app carga la configuración con `app.config.from_object(config_class)`

---

## Archivo modificado
### `app/__init__.py`
```python
from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
import config as app_config

def create_app(config_class=app_config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/'
    )

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
```

**¿Qué cambió exactamente?**

| Línea | Qué hace |
|-------|----------|
| `import config as app_config` | Importa el módulo config.py con un alias para evitar conflicto con el nombre `config` de Flask |
| `config_class=app_config.DevelopmentConfig` | Define `DevelopmentConfig` como configuración por defecto |
| `app.config.from_object(config_class)` | Carga todas las variables de la clase de configuración en la app Flask |


-   **`config_class=app_config.DevelopmentConfig`:**
    +   Le dice a la función `create_app` que, si nadie le especifica una configuración diferente al momento de llamarla, debe usar automáticamente la clase `DevelopmentConfig` que importaste de tu archivo `config.py`.
        *   En tu día a día (desarrollo), usará `DevelopmentConfig`.
        *   Cuando corras los tests, podrías llamarla como `create_app(app_config.TestingConfig)` para usar una base de datos temporal, por ejemplo.

-   **`app.config.from_object(config_class)`:**
    +   Flask toma la clase que le pasaste (en este caso, una clase de Python con variables como `DEBUG = True` o `SECRET_KEY = '...'`) y vuelca todos esos valores dentro del diccionario interno de Flask llamado `app.config`.
        *   Flask busca todas las variables escritas en **MAYÚSCULAS** dentro de esa clase y las registra en el sistema.
        *   Centralizas todo. Si mañana necesitas cambiar la URL de la base de datos o el puerto, no tienes que buscar por todo el código; solo lo cambias en tu archivo config.py y esta línea se encarga de repartir esa información a toda la App.
##  Recordatorio
### `config.py`:
Es un archivo donde guardás todas las variables de configuración de tu app en un solo lugar.  
En vez de tener valores hardcodeados por todo el código, los centralizás acá.
-   `import os` —  os es un módulo de Python que te permite interactuar con el sistema operativo. En tu config.py se usa específicamente para leer variables de entorno con `os.getenv()`:
    +   Busca la variable `SECRET_KEY` en el sistema operativo (que en tu caso viene del `.env` cargado por `load_dotenv()`)
        *   `load_dotenv()` es la función que carga el archivo `.env` y convierte cada línea en una variable de entorno del sistema operativo.
    +   Si la encuentra, la usa
    +   Si no la encuentra, usa el valor por defecto `'default_secret_key'`
-   `SECRET_KEY` — una clave secreta que Flask usa para firmar cookies y tokens
-   `DEBUG` — si está en `True` la app muestra errores detallados, en `False` los oculta
-   En el futuro: la URL de la base de datos, configuración de email, etc.

```
.env                    load_dotenv()              os.getenv()
─────────────────       ──────────────────         ─────────────────
SECRET_KEY=abc123  →    carga el archivo    →      lee SECRET_KEY
FLASK_DEBUG=True        al sistema operativo       y devuelve 'abc123'
```
La idea es tener distintas clases para distintos entornos:
-   `DevelopmentConfig` — para cuando estás desarrollando localmente
-   `ProductionConfig` — para cuando la app está en un servidor real

---

### 3. `run.py`

`run.py` no necesita cambios porque ya llama a `create_app()` sin argumentos, y el parámetro por defecto es `DevelopmentConfig`.

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

---

## ¿Cómo se usa en el futuro?

Gracias a este cambio, en el futuro se puede pasar cualquier configuración:

```python
# Modo desarrollo (por defecto)
app = create_app()

# Modo producción (con MySQL)
app = create_app(config.ProductionConfig)

# Modo testing
app = create_app(config.TestingConfig)
```

---

## Verificación

Después de hacer los cambios, verificar que la app sigue funcionando:

```bash
cd part3
python3 run.py
```

La app debe arrancar en `http://127.0.0.1:5000/api/v1/` sin errores.


---

#   Task 1

---

#   Task 2

---

#   Task 3

---

#   Task 4

---

#   Task 5

---

#   Task 6

---

#   Task 7

---

#   Task 8

---

#   Task 9

---

#   Task 10

---
