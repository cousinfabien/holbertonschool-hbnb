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
---

# Task 1 — Modify the User Model to Include Password Hashing
## ¿Qué es el hashing de contraseñas?

Cuando un usuario se registra, **nunca** se guarda la contraseña tal cual en la base de datos.  
Si alguien accede a la base de datos y ve `password: "micontraseña123"` es un problema de seguridad grave.

En cambio se guarda un **hash**, que es una versión encriptada e irreversible:

```
"micontraseña123"  →  bcrypt  →  "$2b$12$eKbB2dXk..."
```

Cuando el usuario hace login, `bcrypt` compara la contraseña ingresada con el hash guardado.  
**Nunca se puede revertir el hash** para obtener la contraseña original.

---

## ¿Qué es `bcrypt`?

`bcrypt` es un algoritmo de hashing diseñado específicamente para contraseñas. A diferencia de otros algoritmos (como MD5 o SHA), bcrypt es **lento por diseño**, lo que hace que los ataques de fuerza bruta sean mucho más difíciles.

`flask-bcrypt` es el plugin que integra bcrypt con Flask.

---

## Archivos modificados
### 1. `app/__init__.py`
Se registra bcrypt como plugin de la app, igual que se hace con otras extensiones de Flask.

**Antes:**
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

**Después:**
```python
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
import config as app_config

bcrypt = Bcrypt()

def create_app(config_class=app_config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)

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

**¿Por qué `bcrypt = Bcrypt()` está fuera de `create_app()`?**
Porque otros archivos (como `user.py`) necesitan importar `bcrypt` para usarlo. Si estuviera dentro de `create_app()` no sería accesible desde afuera.

**¿Por qué `bcrypt.init_app(app)`?**
Es el patrón estándar de Flask para registrar extensiones.  
-   Primero se crea la extensión vacía (`Bcrypt()`)
-   Se la conecta a la app concreta (`init_app(app)`). 
Esto permite usar la extensión con el Application Factory pattern.



---

### 2. `app/models/user.py`

Se agregan dos métodos al modelo `User`:

**Antes:**
```python
#!/usr/bin/python3
import re
from app.models.base_model import BaseModel

class User(BaseModel):
    def __init__(self, first_name, last_name, email, password="", is_admin=False):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError("Invalid first_name")
        if not last_name or len(last_name) > 50:
            raise ValueError("Invalid last_name")
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.places = []

    def update_profile(self, data):
        """Update user profile with validation"""
        if "first_name" in data:
            if not data["first_name"] or len(data["first_name"]) > 50:
                raise ValueError("Invalid first_name")
        if "last_name" in data:
            if not data["last_name"] or len(data["last_name"]) > 50:
                raise ValueError("Invalid last_name")
        if "email" in data:
            if not data["email"] or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                raise ValueError("Invalid email")
        self.update(data)
```

**Después:**
```python
#!/usr/bin/python3
import re
from app.models.base_model import BaseModel
from app import bcrypt

class User(BaseModel):
    def __init__(self, first_name, last_name, email, password="", is_admin=False):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError("Invalid first_name")
        if not last_name or len(last_name) > 50:
            raise ValueError("Invalid last_name")
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.places = []

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

    def update_profile(self, data):
        """Update user profile with validation"""
        if "first_name" in data:
            if not data["first_name"] or len(data["first_name"]) > 50:
                raise ValueError("Invalid first_name")
        if "last_name" in data:
            if not data["last_name"] or len(data["last_name"]) > 50:
                raise ValueError("Invalid last_name")
        if "email" in data:
            if not data["email"] or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                raise ValueError("Invalid email")
        self.update(data)
```

**¿Qué hace `hash_password()`?**
Toma la contraseña en texto plano, la hashea con bcrypt y la guarda en `self.password`.  
El `.decode('utf-8')` convierte el resultado de bytes a string para poder guardarlo.
-   `bcrypt.generate_password_hash(password)`: 
    +   Toma la contraseña (ej: "`Hola123`") y le aplica un algoritmo matemático complejo.
    +   El resultado es una cadena larga de caracteres aleatorios (el hash).
    +   **Dato curioso**: 
        *   Aunque uses la misma contraseña, `bcrypt` añade un "salt" (una semilla aleatoria) para que el hash siempre sea diferente, aumentando la seguridad.
-   `.decode('utf-8')`: 
    +   El resultado de generar el hash es un objeto de tipo bytes.
    +   Como queremos guardarlo en nuestra base de datos (o en memoria) como una cadena de texto normal, lo decodificamos a UTF-8.
-   `self.password = ...`: 
    +   Finalmente, sobreescribe el atributo de la instancia.
    +   Ahora, en lugar de guardar "`Hola123`", guardas algo como `$2b$12$KIXl.xxx...`.

**¿Qué hace `verify_password()`?**
Compara la contraseña ingresada con el hash guardado.  
Devuelve `True` si coinciden, `False` si no.  
Se usa en el login (Task 2).
-   `bcrypt.check_password_hash(self.password, password)`:
1.   Toma el hash que tienes guardado (`self.password`).
2.   Toma la contraseña que el usuario acaba de escribir en el formulario de login (`password`).
3.   Internamente, `bcrypt` sabe cómo comparar ambas para ver si coinciden sin necesidad de conocer la clave original.
-   `return ...`: Devuelve `True` si coinciden o `False` si el usuario se equivocó.
---

### 3. `app/api/v1/users.py`

Dos cambios:
- El endpoint `POST /api/v1/users/` ahora acepta `password` y la hashea antes de guardar
- Ningún endpoint devuelve el campo `password` en la respuesta

**Antes** (user_model y POST):
```python
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

def post(self):
    """Register a new user"""
    user_data = api.payload
    try:
        new_user = facade.create_user(user_data)
        return {
            'id': new_user.id,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email
        }, 201
    except ValueError as e:
        return {'error': str(e)}, 400
```

**Después:**
```python
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

def post(self):
    """Register a new user"""
    user_data = api.payload
    try:
        new_user = facade.create_user(user_data)
        return {
            'id': new_user.id,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email
        }, 201
    except ValueError as e:
        return {'error': str(e)}, 400
```

**Nota:** la respuesta del POST no incluye `password`. Esto es intencional — nunca se devuelve la contraseña, ni siquiera hasheada.

---

### 4. `app/services/facade.py` — método `create_user`

También hay que actualizar el facade para que hashee la contraseña al crear un usuario.

**Antes:**
```python
def create_user(self, user_data):
    user = User(**user_data)
    self.user_repo.add(user)
    return user
```

**Después:**
```python
def create_user(self, user_data):
    user = User(**user_data)
    user.hash_password(user_data['password'])
    self.user_repo.add(user)
    return user
```

**¿Por qué se hashea en el facade y no en el modelo?**
Porque el `__init__` del modelo acepta `password=""` como valor por defecto (para cuando se crea un usuario sin contraseña en tests). El facade es el punto de entrada desde la API, así que es el lugar correcto para aplicar la lógica de negocio de hashear.

---

## Flujo completo del registro

```
POST /api/v1/users/
    │
    ▼
users.py (API)
    recibe: {first_name, last_name, email, password}
    │
    ▼
facade.create_user(user_data)
    crea User() → hashea password → guarda en repo
    │
    ▼
respuesta: {id, first_name, last_name, email}
    (sin password)
```

---
---

# Task 2 — Implement JWT Authentication
## ¿Qué es JWT?

**JWT (JSON Web Token)** es un sistema de autenticación basado en tokens.  
En vez de guardar sesiones en el servidor, el servidor genera un token firmado que el cliente guarda y envía en cada request.

El token tiene 3 partes separadas por puntos:
```
eyJhbGciOiJIUzI1NiJ9.eyJpZCI6IjEyMyIsImlzX2FkbWluIjpmYWxzZX0.abc123
      HEADER                          PAYLOAD                    SIGNATURE
```

- **Header** — algoritmo de firma
- **Payload** — datos del usuario (id, is_admin, expiración)
- **Signature** — firma generada con el `SECRET_KEY` para verificar que el token no fue modificado

**¿Por qué es seguro?** Si alguien modifica el payload, la firma ya no coincide y el servidor rechaza el token.

---

## Flujo completo de autenticación

```
1. Cliente envía email + password
        │
        ▼
2. API verifica credenciales con verify_password()
        │
        ▼
3. Si son correctas → genera JWT token con create_access_token()
        │
        ▼
4. Cliente recibe el token y lo guarda
        │
        ▼
5. Cliente envía el token en el header de cada request protegido:
   Authorization: Bearer <token>
        │
        ▼
6. @jwt_required() verifica el token automáticamente
        │
        ▼
7. Si es válido → accede al endpoint
   Si no es válido → 401 Unauthorized
```

---

## Archivos modificados

### 1. `app/__init__.py`

Se agrega `JWTManager` igual que se hizo con `bcrypt` en el Task 1.

**Antes (Task 1):**
```python
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
import config as app_config

bcrypt = Bcrypt()

def create_app(config_class=app_config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)

    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/')

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
```

**Después (Task 2):**
```python
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns
import config as app_config

bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=app_config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)

    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/')

    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
```

**¿Por qué `JWTManager` usa `SECRET_KEY` y no `JWT_SECRET_KEY`?**
Porque `flask-jwt-extended` busca primero `JWT_SECRET_KEY` en la config, y si no existe usa `SECRET_KEY`.  
Como ya tenemos `SECRET_KEY` en `config.py` no hace falta agregar nada más.

---

### 2. `app/api/v1/auth.py` (archivo nuevo)

Este archivo no existía. Se crea desde cero con el endpoint de login.

```python
#!/usr/bin/python3
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade

api = Namespace('auth', description='Authentication operations')

# Model for input validation and Swagger documentation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload

        # Step 1: Retrieve the user based on the provided email
        user = facade.get_user_by_email(credentials['email'])

        # Step 2: Check if the user exists and the password is correct
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Step 3: Create a JWT token with the user's id and is_admin flag
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )

        # Step 4: Return the JWT token to the client
        return {'access_token': access_token}, 200
```

**¿Qué es `create_access_token()`?**
Es la función de `flask-jwt-extended` que genera el token JWT. Recibe:
- `identity` — el ID del usuario (como string). Es lo que devuelve `get_jwt_identity()` cuando se verifica el token.
- `additional_claims` — datos extra que queremos guardar en el token, como `is_admin`.

**¿Por qué `identity=str(user.id)` y no solo `user.id`?**
Porque `flask-jwt-extended` requiere que el identity sea un string.

---

### 3. Endpoint de prueba `/api/v1/auth/protected` (opcional)

El task sugiere crear un endpoint de prueba para verificar que el token funciona:

```python
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        """A protected endpoint that requires a valid JWT token"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        return {
            'message': f'Hello, user {current_user_id}',
            'is_admin': claims.get('is_admin', False)
        }, 200
```

**Funciones clave de `flask-jwt-extended`:**

| Función | Qué devuelve |
|---------|-------------|
| `@jwt_required()` | Decorator que bloquea el acceso si no hay token válido |
| `get_jwt_identity()` | El `identity` del token (el ID del usuario) |
| `get_jwt()` | Todos los claims del token (incluye `is_admin`) |

---

## Diferencia entre `get_jwt_identity()` y `get_jwt()`

```python
# get_jwt_identity() devuelve solo el identity
current_user_id = get_jwt_identity()
# → "3fa85f64-5717-4562-b3fc-2c963f66afa6"

# get_jwt() devuelve todos los claims
claims = get_jwt()
# → {
#     "sub": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
#     "is_admin": False,
#     "exp": 1234567890,
#     ...
#   }
is_admin = claims.get('is_admin', False)
```

---

## Resumen de archivos del Task 2

| Archivo | Qué cambia |
|---------|------------|
| `app/__init__.py` | Agregar `JWTManager` + registrar namespace `auth` |
| `app/api/v1/auth.py` | Archivo nuevo con endpoint `POST /api/v1/auth/login` |

---

## Test con cURL

**Login:**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "mipassword"}'
```

**Respuesta:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

**Acceder a endpoint protegido:**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/auth/protected" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..."
```


**Respuesta:**
```json
{
    "message": "Hello, user 3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

##  **`app/__init__.py`**
```python
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT token. Format: Bearer <token>'
    }
}

api = Api(app, version='1.0', title='HBnB API',
          description='HBnB Application API',
          doc='/api/v1/',
          authorizations=authorizations,
          security='Bearer')
```

Este código le dice a Swagger cómo manejar la autenticación JWT.
El diccionario `authorizations` define un esquema de seguridad llamado `'Bearer'` con estas propiedades:
-   `'type': 'apiKey'` — le dice a Swagger que la autenticación es mediante una clave/token
-   `'in': 'header'` — ese token va en el header HTTP (no en la URL ni en el body)
-   `'name': 'Authorization'` — el nombre exacto del header es `Authorization`
-   `'description`' — texto informativo que aparece en la UI de Swagger

El `Api()` es donde se crea la aplicación Flask-RestX, y los dos parámetros nuevos son:
-   `authorizations=authorizations` — le pasa el esquema que definiste arriba
-   `security='Bearer'` — le dice que por defecto todos los endpoints usan ese esquema

El resultado visual es que aparece el botón Authorize 🔓 en Swagger, donde podés pegar tu token una sola vez y Swagger lo incluye automáticamente en todos los requests que hagas desde la UI.
Sin esto, Swagger no sabe que existe autenticación y no puede enviar el header `Authorization` por vos.

---
---

# Task 3 — Places.py: Authenticated Endpoints
## `/v1/places.py`
```python
# 1. Bloquea si no hay token
@jwt_required()          
def post(self):
    # 2. Obtiene el ID del usuario logueado
    current_user = get_jwt_identity()   
    # 3. Lógica de negocio con validaciones de ownership
```

---

### **POST** `/api/v1/places/` — Crear lugar (autenticado)
Agregar autenticación y forzar que `owner_id` sea el usuario logueado, no el que manda el body:
```
token → quién soy → ese soy el owner
```

#### **Importaciones**
```python
from flask_jwt_extended import jwt_required, get_jwt_identity
```

#### **Errores**
```python
@api.response(401, 'Missing or invalid token')
```
#### **Cambios en POST**
```python
@jwt_required()
def post(self):
    current_user = get_jwt_identity()
    place_data['owner_id'] = current_user
```

1. 
```python
# Decorator que bloquea el endpoint si no hay token válido (devuelve 401)
@jwt_required()
``` 
2. 
```python
# get_jwt_identity(): Función que extrae el ID del usuario desde el token
current_user = get_jwt_identity()
# 
place_data = request.json
# fuerza que el owner sea el usuario logueado,
# ignorando cualquier `owner_id` que venga en el body del request
place_data['owner_id'] = current_user
```
**¿Por qué sobreescribir `owner_id`?**
Sin esto, cualquier usuario podría enviar en el body un `owner_id` 
de otra persona y crear un lugar en su nombre.  
Al sobreescribirlo con el token, garantizamos que el owner siempre 
es el usuario autenticado, sin importar lo que venga en el request.


### **PUT** `/api/v1/places/<place_id>` — Actualizar lugar (solo el dueño)
Autenticación + verificar que el lugar te pertenece:
```
token → quién soy → ¿soy el dueño del lugar? → si no, 403
```
#### **Cambios en PUT**
```python
# Bloquea si no hay token → 401
@jwt_required()
def put(self, place_id):
    # get_jwt_identity(): obtiene el ID del usuario logueado
    current_user = get_jwt_identity()
    # Se busca el lugar en la base de datos
    place = facade.get_place(place_id)
    # Primero verificar que el lugar existe
    if place is None:
            return {'error': 'Place not found'}, 404
    # Se compara `place.owner_id` con `current_user` (verificar ownership)
    if place.owner_id != current_user:
        # Si no coinciden → 403 Unauthorized
        return {'error': 'Unauthorized action'}, 403
        # Si coinciden → se permite la actualización
```
### **GET** `/api/v1/places/` y **GET** `/api/v1/places/<place_id>` — Públicos

Sin cambios. No llevan `@jwt_required()` porque cualquier usuario
puede ver los lugares sin estar autenticado.

### Tabla de accesos

| Endpoint     | Sin token | Token pero no es dueño |
|--------------|-----------|------------------------|
| POST /places | 401       | —                      |
| PUT /places  | 401       | 403                    |
| GET /places  | ✅ público | ✅ público             |

---

## `/v1/reviews.py`
```python
# 1. Bloquea si no hay token
@jwt_required()
def post(self):
    # 2. Obtiene el ID del usuario logueado
    current_user = get_jwt_identity()
    # 3. Lógica de negocio con validaciones de ownership
```

---

### POST `/api/v1/reviews/` — Crear review (autenticado)
Autenticación + dos validaciones extra:
```
token → quién soy → ¿soy dueño del lugar? → si sí, 400
                  → ¿ya reviewé este lugar? → si sí, 400
```

#### **Importaciones**
```python
from flask_jwt_extended import jwt_required, get_jwt_identity
```

#### **Errores**
```python
@api.response(201, 'Review successfully created')
@api.response(400, 'Invalid input data')
@api.response(401, 'Missing or invalid token')
```

#### **Cambios en POST**
```python
@jwt_required()
def post(self):
    current_user = get_jwt_identity()
    review_data['user_id'] = current_user
```
1. Decorator
```python
# Decorator que bloquea el endpoint si no hay token válido (devuelve 401)
@jwt_required()
```
2. Forzar `user_id`
```python
# Extrae el ID del usuario desde el token y lo fuerza como user_id
current_user = get_jwt_identity()
review_data = request.json
review_data['user_id'] = current_user
```
3. Verificar `place_id`
```python
# Verifica que el lugar existe antes de cualquier otra validación
place = facade.get_place(review_data['place_id'])
if place is None:
    return {'error': 'Place not found'}, 404
```
4. Dueño no puede dar review a su propio lugar
```python
# El dueño del lugar no puede dar un review a su propio lugar
if place.owner_id == current_user:
    return {'error': 'You cannot review your own place'}, 400
```
5. No se puede dar review al mismo lugar dos veces
```python
# Un usuario no puede reviewar el mismo lugar dos veces
existing_reviews = facade.get_reviews_by_place(review_data['place_id'])
for review in existing_reviews:
    if review.user_id == current_user:
        return {'error': 'You have already reviewed this place'}, 400
```

#### **¿Por qué el orden de las validaciones importa?**
Primero verificamos que el lugar existe (404), luego que no sos el dueño (400),
luego que no reviewaste antes (400). Si lo hacemos al revés podríamos
tener un error al intentar acceder a `place.owner_id` cuando `place` es `None`.

---

### PUT `/api/v1/reviews/<review_id>` — Actualizar review (solo el autor)
Autenticación + verificar que la review es tuya:
```
token → quién soy → ¿creé yo esta review? → si no, 403
```

#### **Cambios en PUT**
```python
# Bloquea si no hay token → 401
@jwt_required()
def put(self, review_id):
    # Obtiene el ID del usuario logueado
    current_user = get_jwt_identity()
    # Primero verificar que la review existe
    r = facade.get_review(review_id)
    if r is None:
        return {'error': 'Review not found'}, 404
    # Verificar que el usuario es el autor
    if r.user_id != current_user:
        # Si no coinciden → 403 Unauthorized
        return {'error': 'Unauthorized action'}, 403
        # Si coinciden → se permite la actualización
```

---

### DELETE `/api/v1/reviews/<review_id>` — Eliminar review (solo el autor)
Misma lógica que el PUT, pero elimina en vez de actualizar:
```
token → quién soy → ¿creé yo esta review? → si no, 403
```

#### **Cambios en DELETE**
```python
# Bloquea si no hay token → 401
@jwt_required()
def delete(self, review_id):
    current_user = get_jwt_identity()
    # Primero verificar que la review existe
    r = facade.get_review(review_id)
    if r is None:
        return {'error': 'Review not found'}, 404
    # Verificar ownership
    if r.user_id != current_user:
        return {'error': 'Unauthorized action'}, 403
    # Si coinciden → eliminar
    facade.delete_review(review_id)
    return {'message': 'Review deleted successfully'}, 200
```

---


### **GET** `/api/v1/reviews/` y **GET** `/api/v1/reviews/<review_id>` — Públicos

Sin cambios. No llevan `@jwt_required()` porque cualquier usuario
puede ver las reviews sin estar autenticado.

---


### **Reviews POST** — autenticación + dos validaciones extra:
```
token → quién soy → ¿soy dueño del lugar? → si sí, 400
                  → ¿ya reviewé este lugar? → si sí, 400
```

### **Reviews PUT y DELETE** — autenticación + verificar que la review es tuya:
```
token → quién soy → ¿creé yo esta review? → si no, 403
```

---
---

## `/v1/users.py`
```python
# 1. Bloquea si no hay token
@jwt_required()
def put(self, user_id):
    # 2. Obtiene el ID del usuario logueado
    current_user = get_jwt_identity()
    # 3. Lógica de negocio con validaciones de ownership
```

---

### PUT `/api/v1/users/<user_id>` — Modificar usuario (solo el propio)
Autenticación + tres verificaciones:
```
token → quién soy → ¿estoy modificando mi propio perfil? → si no, 403
                  → ¿intentás cambiar email o password? → si sí, 400
```

#### **Importaciones**
```python
from flask_jwt_extended import jwt_required, get_jwt_identity
```

#### **Errores**
```python
@api.response(400, 'You cannot modify email or password')
@api.response(403, 'Unauthorized action')
@api.response(404, 'User not found')
```

#### **Cambios en PUT**

1. Decorator
```python
# Decorator que bloquea el endpoint si no hay token válido (devuelve 401)
@jwt_required()
```
2. Extraer el ID del usuario
```python
# Extrae el ID del usuario desde el token
current_user = get_jwt_identity()

# Verifica que el usuario está modificando su propio perfil
if user_id != current_user:
    return {'error': 'Unauthorized action'}, 403
```
3. Prevenir modificar el email o password
```python
# Previene modificar email o password en este endpoint
if 'email' in user_data or 'password' in user_data:
    return {'error': 'You cannot modify email or password'}, 400
```

#### **¿Por qué no se puede modificar email ni password aquí?**
El email y password son datos sensibles que requieren
verificaciones adicionales (como confirmar identidad).
Este endpoint solo permite cambiar datos básicos como
`first_name` y `last_name`.

---

### POST `/api/v1/users/` y GET — Públicos

Sin cambios. El registro de usuarios y la consulta
son públicos porque cualquiera puede crear una cuenta
o ver la lista de usuarios.

---

## Tabla de accesos

| Endpoint   | Sin token  | Token pero no es el usuario |
|------------|------------|-----------------------------|
| PUT /users | 401        | 403                         |
| POST /users| ✅ público  | ✅ público                  |
| GET /users | ✅ público  | ✅ público                  |


---
---

# Task 4 — Administrator Access Endpoints (RBAC)
##  Explicacion
### Concepto
Vamos a gregar un sistema de roles donde los **admins** tienen más permisos que los usuarios normales.
RBAC (Role-Based Access Control) = control de acceso basado en roles.
En este task, el rol es `is_admin` que viene dentro del token JWT.

### ¿Cómo sabe el sistema si sos admin?

En el Task 2, cuando se crea el token se incluye `is_admin`:
```python
access_token = create_access_token(
    identity=str(user.id),
    additional_claims={"is_admin": user.is_admin}
)
```

Para leer ese claim en los endpoints usamos `get_jwt()` en vez de `get_jwt_identity()`:
```python
# get_jwt_identity() → solo devuelve el user_id (string)
current_user_id = get_jwt_identity()

# get_jwt() → devuelve TODOS los claims del token
claims = get_jwt()
is_admin = claims.get('is_admin', False)
```

---

### Diferencia entre get_jwt_identity() y get_jwt()

| Función | Devuelve | Uso |
|---|---|---|
| `get_jwt_identity()` | `"3dfcfef5-..."` (solo el ID) | Verificar ownership |
| `get_jwt()` | `{"sub": "3dfcfef5", "is_admin": true, ...}` | Verificar rol |

---

### Patrón base que se repite en todos los endpoints admin
```python
@jwt_required()
def post(self):
    claims = get_jwt()
    # Si no es admin → 403
    if not claims.get('is_admin'):
        return {'error': 'Admin privileges required'}, 403
    # Si es admin → ejecutar lógica
```

---

### ¿Qué cambia en cada archivo?
#### `users.py` — POST y PUT
- **POST `/api/v1/users/`**: Antes era público, ahora solo admins pueden crear usuarios
- **PUT `/api/v1/users/<user_id>`**: 
  - Usuario normal → solo puede modificar su propio perfil, sin email ni password
  - Admin → puede modificar cualquier usuario, incluyendo email y password

#### `amenities.py` — POST y PUT
- **POST /api/v1/amenities/**: Solo admins pueden crear amenities
- **PUT /api/v1/amenities/<amenity_id>**: Solo admins pueden modificar amenities

#### `places.py` — PUT
- Usuario normal → solo puede modificar sus propios lugares
- Admin → puede modificar cualquier lugar sin importar el owner

#### `reviews.py` — PUT y DELETE
- Usuario normal → solo puede modificar/eliminar sus propias reviews
- Admin → puede modificar/eliminar cualquier review sin importar el autor

---

### Lógica de ownership con bypass para admin
```python
@jwt_required()
def put(self, place_id):
    claims = get_jwt()
    is_admin = claims.get('is_admin', False)
    current_user = get_jwt_identity()

    place = facade.get_place(place_id)
    if place is None:
        return {'error': 'Place not found'}, 404

    # Admin bypasses ownership check
    if not is_admin and place.owner_id != current_user:
        return {'error': 'Unauthorized action'}, 403

    # Continuar con la actualización
```

La clave es `if not is_admin and ...`:
- Si es admin → salta la verificación de ownership
- Si no es admin → verifica que sea el dueño

---

### Problema: ¿Cómo crear el primer admin?

El task lo menciona como punto importante:
> "Discuss different strategies with your team to overcome this problem."

Las opciones son:
1. Insertar un usuario admin directo en la base de datos (Task 9 — SQL scripts)
2. Hardcodear un usuario admin al iniciar la app (solo para desarrollo)
3. Crear un script separado que promueva a un usuario a admin

Por ahora, para testear, vamos a agregar un usuario admin inicial
en el `facade.__init__()` temporalmente.

### Diferencia con Task 3

- Task 3 → verificaba **quién sos** (ownership)
- Task 4 → verifica **qué rol tenés** (is_admin)

---

### Tabla de accesos actualizada

| Endpoint | Sin token | Usuario normal | Admin |
|---|---|---|---|
| POST /users | 401 | 403 | ✅ |
| PUT /users | 401 | Solo el propio (sin email/pass) | Cualquier usuario |
| POST /amenities | 401 | 403 | ✅ |
| PUT /amenities | 401 | 403 | ✅ |
| PUT /places | 401 | Solo el dueño | Cualquier lugar |
| PUT /reviews | 401 | Solo el autor | Cualquier review |
| DELETE /reviews | 401 | Solo el autor | Cualquier review |


## `users.py`: Admin Access
### POST `/api/v1/users/` — Crear usuario (solo admin)
Antes era público. Ahora solo admins pueden crear usuarios.
```
token → ¿is_admin? → si no, 403 → si sí, crear usuario
```

#### **Importaciones nuevas**
```python
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
```
`get_jwt()` es nuevo — devuelve todos los claims del token incluyendo `is_admin`.

#### **Cambios en POST**
```python
@jwt_required()
def post(self):
    claims = get_jwt()
    if not claims.get('is_admin'):
        return {'error': 'Admin privileges required'}, 403
```
1.
```python
# get_jwt() devuelve todos los claims del token
claims = get_jwt()
```
2.
```python
# Si is_admin no existe en el token o es False → 403
if not claims.get('is_admin'):
    return {'error': 'Admin privileges required'}, 403
```

---

### PUT `/api/v1/users/<user_id>` — Modificar usuario
Lógica combinada Task 3 + Task 4:
```
token → ¿is_admin?
    → si NO  → ¿es mi propio perfil? → si no, 403
              → ¿intenta cambiar email/pass? → si sí, 400
    → si SÍ  → puede modificar cualquier usuario
              → verifica uniqueness de email si lo cambia
```

#### **Cambios en PUT**
```python
claims = get_jwt()
is_admin = claims.get('is_admin', False)
current_user = get_jwt_identity()

# Non-admin: solo puede modificar su propio perfil
if not is_admin and user_id != current_user:
    return {'error': 'Unauthorized action'}, 403

# Non-admin: no puede cambiar email ni password
if not is_admin and ('email' in user_data or 'password' in user_data):
    return {'error': 'You cannot modify email or password'}, 400

# Admin: si cambia el email, verificar que no esté en uso
if is_admin and 'email' in user_data:
    existing = facade.get_user_by_email(user_data['email'])
    if existing and existing.id != user_id:
        return {'error': 'Email already in use'}, 400
```

#### **¿Por qué el admin necesita verificar uniqueness de email?**
El admin puede cambiar el email de cualquier usuario, pero no puede
asignarle un email que ya usa otra persona.
El usuario normal no necesita esta verificación porque no puede
cambiar su email en este endpoint.

---

### GET — Públicos
Sin cambios. Cualquier usuario puede ver la lista de usuarios
o los detalles de un usuario específico.

---

### Tabla de accesos

| Endpoint    | Sin token | Usuario normal            | Admin              |
|-------------|-----------|---------------------------|--------------------|
| POST /users | 401       | 403                       | ✅                 |
| PUT /users  | 401       | Solo el propio sin email/pass | Cualquier usuario  |
| GET /users  | ✅ público | ✅ público               | ✅ público         |

---
## `amenities.py`: Admin Access
### POST `/api/v1/amenities/` — Crear amenity (solo admin)
```
token → ¿is_admin? → si no, 403 → si sí, crear amenity
```

### PUT `/api/v1/amenities/<amenity_id>` — Modificar amenity (solo admin)
```
token → ¿is_admin? → si no, 403 → si sí, modificar amenity
```

#### **Importaciones nuevas**
```python
from flask_jwt_extended import jwt_required, get_jwt
```

#### **Cambios en POST y PUT**
```python
@jwt_required()
def post(self):
    claims = get_jwt()
    if not claims.get('is_admin'):
        return {'error': 'Admin privileges required'}, 403
```
El patrón es idéntico en POST y PUT — solo admins pueden
crear o modificar amenities.

#### **¿Por qué amenities son solo para admins?**
Las amenities son datos globales que aplican a todos los lugares
(WiFi, Piscina, Estacionamiento, etc.).
Si cualquier usuario pudiera crearlas, habría duplicados y datos
inconsistentes. Solo el admin gestiona este catálogo.

### GET — Públicos
Sin cambios. Cualquier usuario puede ver las amenities disponibles.

---

### Tabla de accesos

| Endpoint        | Sin token  | Usuario normal | Admin |
|-----------------|------------|----------------|-------|
| POST /amenities | 401        | 403            | ✅    |
| PUT /amenities  | 401        | 403            | ✅    |
| GET /amenities  | ✅ público | ✅ público     | ✅    |

---

## `places.py`: Admin Bypass

### PUT `/api/v1/places/<place_id>` — Modificar lugar (dueño o admin)
```
token → ¿is_admin?
    → si SÍ  → bypasea ownership → puede modificar cualquier lugar
    → si NO  → ¿es el dueño? → si no, 403
```

#### **Importaciones nuevas**
```python
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
```

#### **Cambio clave en PUT**
```python
claims = get_jwt()
is_admin = claims.get('is_admin', False)
current_user = get_jwt_identity()

# Admin bypasses ownership check
if not is_admin and place.owner_id != current_user:
    return {'error': 'Unauthorized action'}, 403
```

#### **¿Por qué `if not is_admin and ...`?**
- Si `is_admin = True` → la condición completa es `False` → no entra al if → bypasea
- Si `is_admin = False` → evalúa el segundo lado → verifica ownership

#### **POST y GET — Sin cambios**
POST sigue siendo para usuarios autenticados (no requiere admin).
GET sigue siendo público.

---

### Tabla de accesos

| Endpoint    | Sin token  | Usuario normal | Admin          |
|-------------|------------|----------------|----------------|
| POST /places| 401        | ✅             | ✅             |
| PUT /places | 401        | Solo el dueño  | Cualquier lugar|
| GET /places | ✅ público | ✅ público     | ✅ público     |

---

## `reviews.py`: Admin Bypass
### PUT `/api/v1/reviews/<review_id>` — Modificar review (autor o admin)
### DELETE `/api/v1/reviews/<review_id>` — Eliminar review (autor o admin)
```
token → ¿is_admin?
    → si SÍ  → bypasea ownership → puede modificar/eliminar cualquier review
    → si NO  → ¿es el autor? → si no, 403
```

#### **Importaciones nuevas**
```python
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
```
`get_jwt` es nuevo en Task 4 — devuelve todos los claims incluyendo `is_admin`.

#### **Cambio clave en PUT y DELETE**
```python
claims = get_jwt()
is_admin = claims.get('is_admin', False)
current_user = get_jwt_identity()

# Admin bypasses ownership check
if not is_admin and r.user_id != current_user:
    return {'error': 'Unauthorized action'}, 403
```

#### **¿Por qué `if not is_admin and ...`?**
- Si `is_admin = True` → la condición completa es `False` → no entra al if → bypasea
- Si `is_admin = False` → evalúa el segundo lado → verifica que sea el autor

#### **POST y GET — Sin cambios**
POST sigue con las mismas validaciones del Task 3.
GET sigue siendo público.

---

### Tabla de accesos

| Endpoint        | Sin token  | Usuario normal | Admin              |
|-----------------|------------|----------------|--------------------|
| POST /reviews   | 401        | ✅ (con validaciones) | ✅ (con validaciones) |
| PUT /reviews    | 401        | Solo el autor  | Cualquier review   |
| DELETE /reviews | 401        | Solo el autor  | Cualquier review   |
| GET /reviews    | ✅ público | ✅ público     | ✅ público         |

---

## Problema: El Primer Admin
### ¿Por qué necesitamos esto?

En el Task 4 protegimos varios endpoints para que solo admins puedan acceder:
- POST /users → solo admin
- POST /amenities → solo admin
- PUT /amenities → solo admin

Pero para testear esto necesitamos un token con `is_admin: true`.
El token se genera en el login, y el login lee `user.is_admin` del usuario.

**El problema:**
```
Para crear un admin necesito ser admin
Para ser admin necesito que alguien me cree como admin
→ Círculo vicioso
```

---

### ¿Cómo se resuelve en producción?

Las opciones reales son:
1. **Script SQL** — insertar un usuario admin directo en la base de datos (Task 9)
2. **Script de consola** — un comando que promueve a un usuario a admin
3. **Variable de entorno** — al arrancar la app, si no hay admins, crear uno automáticamente

### ¿Cómo lo resolvemos ahora para testear?

Agregamos un usuario admin hardcodeado en `facade.__init__()`.
Solo para desarrollo — en producción esto se hace con SQL.

```python
from flask_bcrypt import Bcrypt

_bcrypt = Bcrypt()

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

        # Admin user for testing — remove in production
        admin = User(
            first_name="Admin",
            last_name="User",
            email="admin@hbnb.com",
            password="admin1234",
            is_admin=True
        )
        admin.password = _bcrypt.generate_password_hash("admin1234").decode('utf-8')
        self.user_repo.add(admin)
```

**¿Por qué no usamos `admin.hash_password("admin1234")`?**

El método `hash_password()` del modelo `User` hace internamente `from app import bcrypt` para acceder a la instancia de bcrypt registrada en Flask. Pero en el momento en que `facade.py` se está importando, la app Flask todavía no terminó de inicializarse, lo que genera un **circular import**.

Para evitarlo, se crea una instancia local `_bcrypt = Bcrypt()` directamente en `facade.py`, fuera de la clase. Esta instancia no está ligada a la app Flask pero es suficiente para hashear la contraseña del admin al momento de inicialización.

**¿Por qué _bcrypt con guion bajo?**
El guion bajo es una convención de Python para indicar que es una variable de uso interno del módulo, no pensada para ser importada desde afuera.

```
admin.hash_password()          →  from app import bcrypt  →  circular import ❌
_bcrypt.generate_password_hash()  →  instancia local       →  funciona ✅
```

### Flujo completo para testear
1. Arrancar la app → admin ya existe en memoria
2. Login con admin@hbnb.com / admin1234
3. Recibir token con is_admin: true
4. Usar ese token para probar endpoints de admin

---
---

# Task 5 — Implement SQLAlchemy Repository
## Objetivo

Reemplazar el repositorio en memoria (`InMemoryRepository`) por uno basado en `SQLAlchemy` que persiste los datos en una base de datos SQLite. Los datos ya no se pierden al reiniciar la app.

---

## Contexto

Hasta ahora los datos vivían en un diccionario de Python en memoria:

```
InMemoryRepository → self._storage = {}  →  se borra al reiniciar ❌
```

A partir del Task 5 los datos se guardan en un archivo `SQLite`:

```
SQLAlchemyRepository → development.db  →  persiste entre reinicios ✅
```

**Importante:** En este task solo se crea el repositorio y se configura SQLAlchemy.  
Los modelos todavía NO se mapean a tablas. Eso se hace en el Task 6.

---

## ¿Qué es SQLAlchemy?

`SQLAlchemy` es un ORM (Object-Relational Mapper).  
Permite trabajar con la base de datos usando Python en vez de SQL puro.

```
Sin ORM:   "INSERT INTO users VALUES ('Juan', 'juan@mail.com')"
Con ORM:   user = User(name='Juan', email='juan@mail.com')
           db.session.add(user)
           db.session.commit()
```

`flask-sqlalchemy` es la extensión que integra SQLAlchemy con Flask.

---

## Archivos modificados

| Archivo | Qué cambia |
|---|---|
| `requirements.txt` | Agregar `sqlalchemy` y `flask-sqlalchemy` |
| `config.py` | Agregar `SQLALCHEMY_DATABASE_URI` y `SQLALCHEMY_TRACK_MODIFICATIONS` |
| `app/__init__.py` | Inicializar `SQLAlchemy` con `db = SQLAlchemy()` |
| `app/persistence/repository.py` | Agregar clase `SQLAlchemyRepository` |
| `app/services/facade.py` | Reemplazar `InMemoryRepository` por `SQLAlchemyRepository` |

---

## Paso 1 — `requirements.txt`

Agregar las dos dependencias nuevas:

```txt
flask-bcrypt
flask-jwt-extended
sqlalchemy
flask-sqlalchemy
```

---

## Paso 2 — `config.py`

**Antes:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
```

**Después:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
```

### **¿Qué es `SQLALCHEMY_DATABASE_URI`?**
Es la dirección de la base de datos.  
El formato `sqlite:///development.db` le dice a SQLAlchemy que use un archivo SQLite llamado `development.db` en la carpeta del proyecto.  
Este archivo no existe todavía. Se crea automáticamente la primera vez que ejecutés (Task 8):
```python
db.create_all()
```
```
sqlite:///development.db
│       │  └── nombre del archivo
│       └── ruta relativa al proyecto
└── tipo de base de datos
```

En producción esto cambia a MySQL:
```python
SQLALCHEMY_DATABASE_URI = 'mysql://usuario:password@localhost/hbnb'
```

### **¿Qué es `SQLALCHEMY_TRACK_MODIFICATIONS`?**
Es una función de **Flask-SQLAlchemy** que rastrea cada cambio en los objetos para emitir "señales" (eventos).  
Consume memoria extra y no la necesitamos, así que se desactiva con `False`. 
Si lo dejás en `True` Flask te tira un warning en consola.

---

## Paso 3 — `app/__init__.py`

Se agrega `SQLAlchemy` igual que se hizo con `bcrypt` y `JWTManager`.

**Antes (Task 2):**
```python
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns
import config as app_config

bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=app_config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)

    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/')

    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
```

**Después (Task 5):**
```python
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns
import config as app_config

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

def create_app(config_class=app_config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/')

    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
```

**¿Por qué `db = SQLAlchemy()` está fuera de `create_app()`?**
Por la misma razón que `bcrypt` y `jwt` — otros archivos (los modelos) necesitan importar `db` para definir sus tablas. Si estuviera dentro de `create_app()` no sería accesible desde afuera.

-   `db = SQLAlchemy()` crea la instancia vacía, sin saber nada de Flask todavía. Es como comprar una heladera sin enchufarla.
-   `db.init_app(app)` la conecta a la app Flask. A partir de ese momento db sabe:
    +   Dónde está la base de datos (lee `SQLALCHEMY_DATABASE_URI` del config)
    +   Cuál es el contexto de la app para manejar las conexiones

```python
bcrypt = Bcrypt()      →   instancia vacía
bcrypt.init_app(app)   →   conectada a Flask

jwt = JWTManager()     →   instancia vacía
jwt.init_app(app)      →   conectada a Flask

db = SQLAlchemy()      →   instancia vacía
db.init_app(app)       →   conectada a Flask
```

---

## Paso 4 — `app/persistence/repository.py`

Se agrega la clase `SQLAlchemyRepository` al mismo archivo donde ya existe `InMemoryRepository`.

```python
from app import db
from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}

    def add(self, obj):
        self._storage[obj.id] = obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        return next(
            (obj for obj in self._storage.values()
             if getattr(obj, attr_name, None) == attr_value),
            None
        )


class SQLAlchemyRepository(Repository):
    def __init__(self, model):
        self.model = model

    def add(self, obj):
        db.session.add(obj)
        db.session.commit()

    def get(self, obj_id):
        return self.model.query.get(obj_id)

    def get_all(self):
        return self.model.query.all()

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()

    def delete(self, obj_id):
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()

    def get_by_attribute(self, attr_name, attr_value):
        return self.model.query.filter_by(**{attr_name: attr_value}).first()
```

### Comparación: InMemoryRepository vs SQLAlchemyRepository

| Método | InMemoryRepository | SQLAlchemyRepository |
|---|---|---|
| `add` | `self._storage[obj.id] = obj` | `db.session.add(obj)` + `commit()` |
| `get` | `self._storage.get(obj_id)` | `Model.query.get(obj_id)` |
| `get_all` | `list(self._storage.values())` | `Model.query.all()` |
| `update` | `setattr(obj, key, value)` | `setattr` + `commit()` |
| `delete` | `del self._storage[obj_id]` | `db.session.delete(obj)` + `commit()` |
| `get_by_attribute` | itera con `getattr` | `Model.query.filter_by()` |

**¿Qué es `db.session`?**
Es la transacción activa de SQLAlchemy.  
Funciona como una "bolsa de cambios" que acumula operaciones y las aplica todas juntas cuando hacés `commit()`.

```
db.session.add(obj)    →  agrega el objeto a la bolsa (no escribe aún)
db.session.delete(obj) →  marca el objeto para borrar (no escribe aún)
db.session.commit()    →  escribe todos los cambios en la base de datos (escribe en el .db)
```

**¿Por qué update no tiene `db.session.add()`?**
Porque el objeto ya está en la sesión — SQLAlchemy lo está rastreando desde que lo trajiste con query.get(). Entonces solo necesitás commit() para guardar los cambios:
```python
obj = self.get(obj_id)        # SQLAlchemy empieza a rastrear obj
setattr(obj, 'name', 'WiFi')  # modificás el objeto
db.session.commit()           # SQLAlchemy detecta el cambio y lo guarda
```

**¿Qué es `Model.query`?**
Es la interfaz de consultas de SQLAlchemy.  
Permite buscar registros sin escribir SQL:

```python
User.query.get("abc-123")                    # SELECT * WHERE id = 'abc-123'
User.query.all()                             # SELECT * FROM users
User.query.filter_by(email="a@b.com").first()# SELECT * WHERE email = 'a@b.com' LIMIT 1
```

**¿Por qué `SQLAlchemyRepository` recibe `model` como parámetro?**
Para que sea reutilizable con cualquier entidad. En vez de tener un repositorio por cada modelo, se crea uno solo que acepta el modelo como argumento:

```python
self.user_repo     = SQLAlchemyRepository(User)
self.place_repo    = SQLAlchemyRepository(Place)
self.review_repo   = SQLAlchemyRepository(Review)
self.amenity_repo  = SQLAlchemyRepository(Amenity)
```

---

## Paso 5 — `app/services/facade.py`

Se reemplaza `InMemoryRepository` por `SQLAlchemyRepository` en el `__init__` de la Facade.

**Antes:**
```python
from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo    = InMemoryRepository()
        self.place_repo   = InMemoryRepository()
        self.review_repo  = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
```

**Después:**
```python
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.persistence.repository import SQLAlchemyRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo    = SQLAlchemyRepository(User)
        self.place_repo   = SQLAlchemyRepository(Place)
        self.review_repo  = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
```

**¿Por qué se eliminó el admin hardcodeado?**
El admin hardcodeado funcionaba con `InMemoryRepository` porque se podía insertar un objeto Python directo en el diccionario. Con `SQLAlchemyRepository` los datos se guardan en la base de datos, y la base de datos todavía no está inicializada en este task. El admin se creará en el Task 9 con un script SQL.
**¿Para qué servía _bcrypt = Bcrypt()?**
Era la solución al circular import. `hash_password()` del modelo User hace internamente `from app import bcrypt`, pero cuando facade.py se importa al arrancar la app, ese `bcrypt` todavía no está listo → circular import.
La solución fue crear una instancia local `_bcrypt = Bcrypt()` directamente en `facade.py` para hashear la contraseña del admin sin pasar por `app`:
```python
# En vez de esto (circular import):
admin.hash_password("admin1234")
# Se hacía esto (instancia local):
admin.password = _bcrypt.generate_password_hash("admin1234").decode('utf-8')
```


---

## ¿Por qué no se puede testear todavía?

En este task solo se creó la infraestructura. Para que `SQLAlchemyRepository` funcione, los modelos (`User`, `Place`, etc.) necesitan estar mapeados a tablas de la base de datos con columnas definidas. Eso se hace en el Task 6.

```
Task 5: Crear SQLAlchemyRepository  ✅
Task 6: Mapear modelos a tablas     ← necesario para que funcione
Task 7: Relaciones entre tablas
Task 8: Inicializar la base de datos
```

---

## Flujo completo después del Task 5

```
Request HTTP
    │
    ▼
API (Namespace)
    │
    ▼
Facade
    │
    ▼
SQLAlchemyRepository
    │
    ▼
db.session.add() / query.get() / etc.
    │
    ▼
development.db (SQLite)
```
## El Task 5 está completo:El Task 5 está completo:





---

## 🏆 Resultado Final del Task 5
✅ `requirements.txt` — agregadas las dependencias
✅ `config.py` — `SQLALCHEMY_DATABASE_URI` y `SQLALCHEMY_TRACK_MODIFICATIONS`
- `SQLAlchemyRepository` implementado siguiendo la misma interfaz que `InMemoryRepository`
✅ `app/__init__.py` — `db = SQLAlchemy()` + `db.init_app(app)`
- `db = SQLAlchemy()` registrado en `app/__init__.py`
- `config.py` actualizado con `SQLALCHEMY_DATABASE_URI` apuntando a `development.db`
✅ `repository.py` — `SQLAlchemyRepository` agregado
✅ `facade.py` — repos cambiados a `SQLAlchemyRepository`
- Facade refactorizada para usar `SQLAlchemyRepository` en todos los repos
- La app todavía no funciona completamente hasta que los modelos sean mapeados (Task 6)

---
---

#   Task 6

---
---

#   Task 7

---
---

#   Task 8

---
---

#   Task 9

---
---

#   Task 10

---
