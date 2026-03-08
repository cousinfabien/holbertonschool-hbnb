# 📝 Registro de Proyecto: HBnB Evolution - Julian

Este documento detalla mi progreso, decisiones de diseño y ejecución técnica durante el desarrollo del proyecto HBnB Evolution.

---

# 🏛️ Parte 1: Diseño de Arquitectura y Documentación

En esta fase inicial, el objetivo fue planificar la estructura completa de la aplicación antes de escribir una sola línea de código. Nos centramos en el diseño conceptual y la lógica de negocio.

#### . El Factory Pattern (`app/__init__.py`)
-   `from flask import Flask`: Importa el framework web principal. Es el que se encarga de recibir las peticiones HTTP (GET, POST, etc.).
-   `from flask_restx import Api`: Importa una extensión poderosa para Flask que facilita la creación de APIs REST y genera automáticamente la documentación Swagger.
-   `create_app()`: Funcion para instanciar Flask.
-   `app = Flask(__name__)`: Crea la instancia del servidor. El parámetro __name__ le ayuda a Flask a saber dónde están los archivos de plantillas o carpetas del proyecto.
-   `api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/api/v1/')`:
    +   `app`: Le dices a la extensión `Api` que debe trabajar sobre tu servidor Flask.
    +   `title` y `description`: Es lo que verás en el encabezado de la página web de documentación.
    +   `doc='/api/v1/'`: Esta es la parte más útil. Indica que si escribes `http://127.0.0.1:5000/api/v1/` en tu navegador, verás el Swagger UI (una lista de todos tus endpoints donde puedes probar si funcionan sin usar Postman).
-   Sin este código, el servidor no sabría cómo responder a las llamadas de internet. Al usar `Flask-RestX`, nos ahorramos mucho trabajo documentando el proyecto, ya que la página web se crea sola a medida que vamos programando los modelos de `User`, `Place`, etc.
-   Evita problemas de importación circular y nos permite configurar diferentes versiones de la app (una para desarrollo y otra para pruebas) de manera sencilla.
-   **Los Placeholders (Comentarios):**
    +   Un **Namespace** es como una carpeta que agrupa rutas. Por ejemplo, el namespace de `users` agrupará: `POST /users`, `GET /users/id`, etc.
### 1. Diagramas de Paquetes
Definimos una arquitectura en capas para asegurar la modularidad:
* **Capa de Presentación (API):** Gestión de endpoints.
* **Capa de Lógica de Negocio (Services/Models):** Donde residen las reglas y entidades.
* **Capa de Persistencia:** Gestión de datos.

### 2. Diagramas de Clase (UML)
Diseñamos la estructura de los datos utilizando el concepto de **Herencia**. 
* **BaseModel:** Clase padre con `id` (UUID4), `created_at` y `updated_at`.
* **Entidades:** `User`, `Place`, `Review` y `Amenity`.

### 3. Diagramas de Secuencia
Modelamos cómo interactúan los objetos para procesos clave:
* Registro de usuario.
* Creación de un lugar.
* Envío de reseñas.
* Búsqueda de lugares.

---
---

# ⚙️ Parte 2: Implementación de la Capa de Negocio y API
## 🚀 Task 0: Configuración del Proyecto e Inicialización
### **Resumen del Task**
En esta etapa, establecí la infraestructura base del proyecto siguiendo una arquitectura de software profesional. El objetivo no era crear funcionalidad aún, sino construir el "contenedor" donde vivirá toda la lógica.

**Logros clave:**
* **Arquitectura en Capas:** Organicé el código en `Presentation` (API), `Business Logic` (Services/Models) y `Persistence`.
* **Patrón Facade:** Implementé el orquestador central (`HBnBFacade`) que servirá como único punto de entrada para las operaciones de negocio.
* **Repositorio Abstracto:** Creé una interfaz de repositorio que permite que el sistema sea independiente de la base de datos (actualmente usa almacenamiento en memoria).
* **Entorno Flask:** Configuré la aplicación con `Flask-RestX` para generar documentación interactiva (Swagger) automáticamente.

---
### **Estructura del Proyecto y Propósito de los Directorios**
La organización del proyecto sigue un esquema modular para asegurar la escalabilidad y el mantenimiento:

* **`app/`**: Contiene el código central de la aplicación.
* **`app/api/`**: Subdirectorio que aloja los endpoints de la API, organizados por versión (ej. `v1/`). Representa la **Capa de Presentación**.
* **`app/models/`**: Contiene las clases de la lógica de negocio (ej. `user.py`, `place.py`). Aquí se definen los objetos y sus reglas.
* **`app/services/`**: Es donde se implementa el **Patrón Facade (Fachada)**, encargado de gestionar la interacción y comunicación entre las diferentes capas.
* **`app/persistence/`**: Subdirectorio donde se implementa el **Repositorio en Memoria**. En la Parte 3, esto será sustituido por una solución con base de datos utilizando SQL Alchemy.
* **`run.py`**: El punto de entrada principal para ejecutar la aplicación Flask.
* **`config.py`**: Se utiliza para configurar las variables de entorno y los ajustes de la aplicación (modo desarrollo, producción, etc.).
* **`requirements.txt`**: Lista todos los paquetes y librerías de Python necesarios para el proyecto.
* **`README.md`**: Contiene una descripción general y breve del proyecto.

---

## **Task 0**

---

### 1. El Factory Pattern (`app/__init__.py`)
-   `from flask import Flask`: Importa el framework web principal. Es el que se encarga de recibir las peticiones HTTP (GET, POST, etc.).
-   `from flask_restx import Api`: Importa una extensión poderosa para Flask que facilita la creación de APIs REST y genera automáticamente la documentación Swagger.
-   `create_app()`: Funcion para instanciar Flask.
-   `app = Flask(__name__)`: Crea la instancia del servidor. El parámetro __name__ le ayuda a Flask a saber dónde están los archivos de plantillas o carpetas del proyecto.
-   `api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/api/v1/')`:
    +   `app`: Le dices a la extensión `Api` que debe trabajar sobre tu servidor Flask.
    +   `title` y `description`: Es lo que verás en el encabezado de la página web de documentación.
    +   `doc='/api/v1/'`: Esta es la parte más útil. Indica que si escribes `http://127.0.0.1:5000/api/v1/` en tu navegador, verás el Swagger UI (una lista de todos tus endpoints donde puedes probar si funcionan sin usar Postman).
-   Sin este código, el servidor no sabría cómo responder a las llamadas de internet. Al usar `Flask-RestX`, nos ahorramos mucho trabajo documentando el proyecto, ya que la página web se crea sola a medida que vamos programando los modelos de `User`, `Place`, etc.
-   Evita problemas de importación circular y nos permite configurar diferentes versiones de la app (una para desarrollo y otra para pruebas) de manera sencilla.
-   **Los Placeholders (Comentarios):**
    +   Un **Namespace** es como una carpeta que agrupa rutas. Por ejemplo, el namespace de `users` agrupará: `POST /users`, `GET /users/id`, etc.

---

### 2. La Interfaz del Repositorio (`repository.py`)
Utilizamos **Clases Base Abstractas (ABC)** para definir un estándar.
-   `class Repository(ABC)`:
    +   `ABC` (Abstract Base Class): Al heredar de ABC, estamos creando una "plantilla" o contrato.
-   `@abstractmethod`: Estos decoradores indican que cualquier clase que quiera ser un **"Repositorio"** está obligada a implementar estos métodos.
-   `InMemoryRepository`: Es la versión "de prueba" que estamos usando ahora.
    +   `self._storage = {}`: diccionario de Python.
        *   La **llave** es el `ID` único del objeto (como el UUID de un usuario).
        *   El **valor** es el objeto completo (`User`, `Place`, etc.).
    +   `add(self, obj)`:
        *   Guarda el objeto en el diccionario usando su `id` como referencia.
    +   `get`
    +   `get_all`
    +   `update(self, obj_id, data)`:
        *   Primero busca el objeto por su `ID`. Si lo encuentra, llama al método `update` interno del objeto (que creamos en el `BaseModel`) para actualizar sus campos.
    +   `delete` 
    +   `get_by_attribute`
        *   `getattr(obj, attr_name)`
        *   Busca dentro de un objeto un atributo por su nombre (como "email").
        *   Ejemplo: Si buscas un usuario por email, este método recorre todos los usuarios guardados hasta encontrar el que coincida
-   Si en el futuro decides cambiar de guardar datos en un diccionario a guardarlos en una base de datos SQL, la API no se enterará, porque ambas clases tendrán exactamente los mismos métodos.
-   **Ventajas**:
    +   **Desacoplamiento**: La lógica de tu aplicación (la Facade) no sabe cómo se guardan los datos, solo sabe que el repositorio tiene un método `.add()`.

    +   **Facilidad de Testing**: Es mucho más rápido probar el código usando un diccionario en memoria que conectándose a una base de datos real.

    +   **Flexibilidad**: En la Parte 3 del proyecto, crearás un `SQLRepository`. Como ambos heredan de `Repository(ABC)`, cambiar uno por otro será tan fácil como cambiar una sola línea de código en tu configuración.

---

### 3.1. La Fachada (`facade.py`)
-   Es el mediador entre la API y la lógica interna.
-   La Fachada contiene las instancias de los repositorios de usuarios, lugares, reseñas y comodidades. Cuando la API recibe una petición, le pide a la Fachada que la procese.
-   Mantiene la capa de la API "limpia". La API solo se encarga de recibir/enviar datos, mientras que la Fachada decide *cómo* se guardan o validan.
-   `__init__`: Al crear una instancia de la Fachada, automáticamente se crean cuatro "almacenes" (repositorios) independientes en la memoria:
    +   `self.user_repo = InMemoryRepository()`
    +   `self.place_repo = InMemoryRepository()`
    +   `self.review_repo = InMemoryRepository()`
    +   `self.amenity_repo = InMemoryRepository()`
    +   Aunque todos usan la misma clase `InMemoryRepository`, cada uno tiene su propio diccionario `_storage`. Así, los usuarios no se mezclan con los lugares o las reseñas.
-   Los Métodos Placeholder (`create_user`,`get_place`)
    +   Un `Placeholder` es un "espacio reservado".
    +   Esto permite que el equipo pueda trabajar en la API sabiendo que el método `create_user` existirá, aunque todavía no esté terminado.
-   Si el día de mañana la lógica para crear un usuario cambia (por ejemplo, ahora hay que enviar un email de bienvenida), solo cambias el código dentro de la Fachada. La API (los archivos en `api/v1/`) no tiene que cambiar nada, porque ella solo llama a `facade.create_user()`.
-   En lugar de que la API tenga que importar 4 repositorios diferentes y saber cómo funciona cada uno, solo importa la Fachada y le pide lo que necesita.

La **HBnBFacade** centraliza el acceso a los datos. Es la encargada de recibir la información cruda de la API, transformarla en objetos de nuestros modelos (como `User` o `Place`) y enviarlos al repositorio correspondiente para que se guarden.

---

### 3.2. La Fachada (`services/__init__.py`)
-   `facade = HBnBFacade()`:
    +   Estamos creando un objeto real a partir de la clase `HBnBFacade` que definimos antes.
    +   Al crear esta instancia aquí, se inicializan los repositorios (`user_repo`, `place_repo`, etc.). Como están en memoria (diccionarios), esta variable `facade` es la que guardará todos tus datos mientras el servidor esté corriendo.
    +   Si cada vez que un usuario se registra creáramos una "nueva" fachada (`facade = HBnBFacade()`), se crearían repositorios nuevos y vacíos. El usuario que guardaste hace un segundo desaparecería.
    +   Al crearla una sola vez, todos los archivos de tu API importarán la misma instancia. Así, si el archivo `users.py` guarda un usuario, cuando `places.py` lo busque, lo encontrará porque ambos están consultando el mismo objeto `facade`.

**Flujo de Trabajo en la Arquitectura:**
1.   **API**: Importa `facade` desde `app.services`.
2.   **API**: Recibe datos y llama a `facade.create_user(datos)`.
3.   **Facade**: Valida y guarda en `self.user_repo`.
4.   **Repositorio**: Almacena el objeto en el diccionario.

---

### 4. El Punto de Entrada (`run.py`)
El archivo `run.py` es el "script de arranque" de la aplicación. Su única responsabilidad es poner en marcha el servidor web de Flask.
-   Importa la función "fábrica" (`create_app`) que configuramos en el paquete `app`. Al ejecutar `app = create_app()`, cargamos en memoria toda la configuración de la API, las rutas y la Fachada.
-   `if __name__ == '__main__'`:
    +   Esta es una convención de Python. Asegura que el servidor solo se inicie si ejecutas el archivo directamente desde la terminal (`python3 run.py`).
    +   Si en el futuro otro script importa algo de `run.py`, no queremos que accidentalmente se encienda un servidor web extra. Solo se "dispara" cuando tú lo decides manualmente.
-   `app.run(debug=True)`:
    +   `app.run()`:
        *   Inicia el servidor local en el puerto predeterminado (normalmente el 5000).
    +   `debug=True`**(Modo Depuración**):
        *   **Auto-reload**: Cada vez que guardas un cambio en cualquier archivo .py, el servidor se reinicia solo. No tienes que cerrarlo y abrirlo manualmente.
        *   **Debugger**: Si hay un error, la terminal (y el navegador) te mostrarán exactamente en qué línea falló y por qué, en lugar de darte un error genérico.

---

### 5. Gestión de Configuración (`config.py`)
El archivo `config.py` permite que la aplicación se comporte de manera diferente dependiendo de dónde se esté ejecutando (en la computadora para desarrollo o en un servidor real para producción).
-   **Uso**:
    +   Intenta leer una variable llamada `SECRET_KEY` desde el sistema operativo. Si no la encuentra, usa `'default_secret_key'` como respaldo.
    +   Esto es vital para no escribir contraseñas reales directamente en el código que subes a GitHub. Las claves sensibles se guardan en el entorno del sistema.
-   **Jerarquía de Clases (Herencia)**:
    +   `class Config`: Es la configuración base. Por seguridad, el modo `DEBUG` siempre está en `False` por defecto.
    +   `class DevelopmentConfig(Config)`: Hereda todo de la clase base, pero cambia `DEBUG` a `True`. Esto es lo que usas mientras programas para ver errores detallados.
-   **El Diccionario de Configuración**:
    +   Crea un mapa que facilita a la aplicación seleccionar qué ajustes cargar. En `app/__init__.py`, podrías decirle a Flask: "Carga los ajustes de 'development'", y él sabrá exactamente qué clase usar.
-   **Importancia**:
    +   Si en la Parte 3 necesitas añadir una base de datos, simplemente agregarás `SQLALCHEMY_DATABASE_URI` aquí adentro.
    +   Evita que los ajustes técnicos estén dispersos por todos los archivos del proyecto. Todo lo que define "cómo" corre la app está en este archivo.

---

### 6. Documentación y Gestión de Dependencias (`README.md` & `requirements.txt`)
Para que el proyecto sea reproducible por cualquier miembro del equipo (o por los correctores de Holberton), definimos los requisitos y los pasos de ejecución.

-   **Guía de Estructura de Archivos (`README.md`)**:
Este es el mapa de navegación del proyecto que incluí en el `README.md` principal:
| Archivo / Directorio | Propósito |
| :--- | :--- |
| `app/api/v1/` | Define las rutas (endpoints) de la API |
| `app/models/` | Contiene las clases de lógica de negocio (User, Place, etc.) |
| `app/services/` | Implementa el Patrón Facade para comunicar capas |
| `app/persistence/` | Almacenamiento de datos (Repositorio en memoria) |
| `config.py` | Ajustes de entorno (Desarrollo/Producción). |
| `run.py` | Script principal para arrancar el servidor. |

-   **Gestión de Librerías `requirements.txt`**: El archivo contiene las dependencias mínimas para que el núcleo de la API funcione:
    +   `flask`: El framework web.
    +   `flask-restx`: Extensión para la creación de APIs REST y Swagger.
-   **Comando para instalar todo el entorno:**
```bash
pip install -r requirements.txt
```

---

### 8. Ejecución de la Aplicación:
Para levantar el servidor y empezar a probar los endpoints, se utiliza el punto de entrada configurado:
```bash
python run.py
```
Una vez ejecutado, la API y su documentación interactiva estarán disponibles en: http://127.0.0.1:5000/api/v1/

---
---

##  **Task 1: Implementación de la Lógica de Negocio (Clases Core)**
Desarrollar las clases `User`, `Place`, `Review` y `Amenity` utilizando Herencia y validaciones estrictas.

-   **Identificadores Únicos (UUID)**: Implementé el uso de UUID4 en lugar de IDs secuenciales por tres razones clave:
1.   **Seguridad**: Evita que usuarios malintencionados adivinen IDs de otros recursos.
2.   **Unicidad Global**: Facilita la futura migración a sistemas distribuidos.
3.   **Escalabilidad**: Permite generar IDs sin necesidad de consultar una base de datos centralizada.
-   **Gestión de Timestamps**: Cada objeto registra automáticamente su `created_at` al nacer y actualiza su `updated_at` cada vez que se usa el método `save()`.

-   **Relaciones entre Entidades**:
    +   **One-to-Many**: Un usuario puede tener muchos lugares; un lugar puede tener muchas reseñas.
    +   **Many-to-Many**: Un lugar puede tener múltiples comodidades (Amenities).

---

### **1. La Clase Base (app/models/base_model.py)**
Evitar tener que escribir los mismos atributos basicos (ID y fechas) una y otra vez en `User`, `Place`, etc.
#### **El Constructor `(`__init__`)`**
Cada vez que creas un nuevo objeto (un usuario, una habitación, etc.), se ejecutan estas tres líneas:
-   **`self.id = str(uuid.uuid4())`**: Genera un identificador único universal. Al convertirlo a `str`, nos aseguramos de que sea fácil de guardar en el Repositorio en Memoria y compatible con JSON más adelante.
-   **`self.created_at`**: Captura el momento exacto (fecha y hora) en que el objeto nace. Este valor no debería cambiar nunca.
-   **`self.updated_at`**: Inicialmente es igual a la fecha de creación, pero cambiará cada vez que modifiquemos el objeto.
#### **El Método `save()`**
-   Simplemente actualiza `self.updated_at` con la hora actual.
-   Es una forma de auditoría. Nos permite saber cuándo fue la última vez que se editó un registro sin tener que actualizar la fecha manualmente cada vez.
#### **El Método `update(self, data)`**
Este es uno de los métodos más potentes de tu arquitectura:
* **`data`**: Es un diccionario que contiene los nuevos valores (ej: `{'first_name': 'Julián'}`).
* **`hasattr(self, key)`**: Es una medida de seguridad. Verifica si el objeto realmente tiene ese atributo antes de intentar cambiarlo. Así evitamos que alguien intente "inyectar" atributos que no pertenecen al modelo.
* **`setattr(self, key, value)`**: Cambia el valor del atributo de forma dinámica.
* **Llamada a `self.save()`**: Al final de la actualización, llama automáticamente a `save()` para que la fecha de modificación quede registrada.

---

### **2. Implementación de Relaciones entre Entidades**
En esta fase del diseño, establecimos cómo interactúan los objetos entre sí en la memoria. Al no usar aún una base de datos relacional (SQL), las relaciones se gestionan mediante **referencias a objetos** y **listas**.

#### **Tipos de Relaciones Implementadas:**

1.  **Usuario y Lugar (One-to-Many):**
    * Un usuario (`User`) puede ser dueño de múltiples lugares (`Place`).
    * En la clase `Place`, el atributo `owner` guarda directamente la instancia del usuario creador.
2.  **Lugar y Reseña (One-to-Many):**
    * Un lugar puede tener muchas reseñas (`Review`).
    * La clase `Place` tiene una lista `self.reviews` para almacenar los objetos de tipo reseña. A su vez, cada reseña conoce a su autor (`user`) y el lugar que califica (`place`).
3.  **Lugar y Comodidad (Many-to-Many):**
    * Un lugar puede tener muchas comodidades (`Amenity`), y una comodidad (ej. "Wi-Fi") puede estar en muchos lugares.
    * Se implementó mediante una lista `self.amenities` dentro de `Place`.

#### **Código: Clase `Place` con Integridad de Datos**

Para cumplir con el requisito de **mantener la integridad de los datos**, añadimos validaciones de tipo (`isinstance`) en los métodos para asegurar que no se agreguen strings o números por error, sino los objetos correctos.  
**Importancia**
Si la API recibe una petición para agregar una reseña, pero por error recibe un texto simple (ej. `"Excelente lugar"`), el método add_review lo rechazaría antes de guardarlo. Esto previene que nuestra lista `self.reviews` se contamine con datos incorrectos que harían fallar la aplicación más adelante.

---

### **3. Pruebas Unitarias de las Clases Core (Independientes)**

Antes de integrar la lógica de negocio con la capa de la API, es fundamental realizar pruebas independientes (Unit Testing) para garantizar que los modelos funcionan de forma aislada y que las aserciones (`assert`) se cumplen.

Para mantener las buenas prácticas del proyecto, creé un directorio dedicado llamado `tests/` separando el código de prueba del código de producción.

#### **Metodología de Pruebas**
1. **Test de Creación de Usuario (`test_user_creation`):**
   * Instancia un objeto `User` con datos de prueba.
   * Valida mediante `assert` que los atributos se asignen correctamente.
   * Confirma que el valor por defecto de `is_admin` sea estrictamente `False`.

2. **Test de Creación de Lugares y Relaciones (`test_place_creation`):**
   * Crea un usuario "Dueño" y un objeto `Place` vinculado a él.
   * Instancia un objeto `Review` y utiliza el método `add_review()` del lugar.
   * Verifica no solo los atributos básicos (como el precio), sino que afirma (`assert len(place.reviews) == 1`) que la relación One-to-Many se estableció correctamente en la memoria.

3. **Test de Comodidades (`test_amenity_creation`):**
   * Valida la correcta instanciación de un `Amenity` simple (ej. "Wi-Fi").

**Resultado:** Todas las clases instancian correctamente sus UUIDs, heredan los timestamps de `BaseModel` y gestionan sus relaciones en memoria sin arrojar excepciones, asegurando la integridad de los datos para la siguiente fase.

### **4. Documentación de la Implementación (`README.md`)**
* **Descripción de Entidades:** Detallé el propósito y las responsabilidades de cada clase central (`User`, `Place`, `Review`, `Amenity`).
* **Ejemplos de Uso:** Incluí fragmentos de código que demuestran cómo instanciar estas clases y cómo ejecutar sus métodos principales (por ejemplo, cómo asociar una `Review` a un `Place` usando el método `add_review`).

---

### **🏆 Resultado Final del Task 1 (Expected Outcome)**

Al concluir esta etapa, el núcleo de la aplicación (Core Business Logic) está completamente estructurado y operativo. Los logros técnicos y arquitectónicos incluyen:

1. **Modelos 100% Funcionales:** Las clases `User`, `Place`, `Review` y `Amenity` están completamente implementadas con sus atributos correctos, UUIDs únicos y gestión automática de timestamps (`created_at`, `updated_at`).
2. **Integridad de Datos Garantizada:** Las clases cuentan con las validaciones internas necesarias (tipos de datos, rangos de valores, etc.) para mantener un estado consistente.
3. **Relaciones Operativas:** Las interacciones entre entidades funcionan sin problemas en la memoria, permitiendo vincular fluidamente dueños a lugares, reseñas a lugares y comodidades a lugares.
4. **Preparación para la Siguiente Capa:** Con esta base sólida, la lógica de negocio está totalmente preparada para integrarse con la **Capa de Presentación** (los endpoints de la API) en la siguiente fase, y eventualmente con la **Capa de Persistencia** (Base de datos) en la Parte 3 del proyecto.

---
---

##  **Task 2**
### 1. Paso 1: Confirmar la Fachada (`app/services/facade.py`)
```Python
from app.persistence.repository import InMemoryRepository
from app.models.user import User

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()

    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)
```
1) **La Inicialización**
-   Importamos `InMemoryRepository` y `User`
-   Cuando la aplicación arranca, creamos una instancia del repositorio en memoria y se la asignamos a `self.user_repo`. Aquí es donde vivirán temporalmente todos los usuarios mientras la app esté encendida.
2) **Crear un Usuario**
-   `user_data`: Es un diccionario que llegará desde la web (ej. `{"first_name": "Julian", "email": "..."}`).
-   `**user_data`: Es un truco de Python (desempaquetado). En lugar de escribir `User(first_name=user_data['first_name'], email=...)`, los asteriscos extraen todo el diccionario y se lo pasan al modelo `User` automáticamente.
-   Finalmente, lo guarda en el repositorio con `.add(user)` y devuelve el objeto recién creado.

3)  **Búsquedas Directas**
Estos métodos son intermediarios puros. Simplemente le piden al repositorio que busque un usuario por su ID o que devuelva la lista completa, y se lo pasan a la API.

4) **Búsqueda por Email (Validación)**
```Python
def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)
```
-   Cuando alguien intente registrarse, la API usará este método para preguntar: "¿Ya existe alguien con este correo?". 
-   El repositorio buscará por el atributo `email`.
5) **Actualizar un Usuario**
```Python
    def update_user(self, user_id, user_data):
        """
        Update an existing user.
        Returns None if user does not exist.
        Raises ValueError if email already exists.
        """
        user = self.user_repo.get(user_id)

        if not user:
            return None

        # Check email uniqueness if modified
        if "email" in user_data:
            existing_user = self.get_user_by_email(user_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")

        # Proceed with the update for all provided attributes regardless of the email check
        updated_user = self.user_repo.update(user_id, user_data)
        return updated_user
```
-   Toma el ID del usuario y el diccionario con los datos nuevos. 
-   Se los pasa al repositorio para que haga la actualización (modificando la memoria y actualizando el `updated_at`). 
-   Luego, busca al usuario ya modificado y lo devuelve para que la API pueda mostrarlo en la pantalla.
---

### 2. Crear los Endpoints (`app/api/v1/users.py`)
```Python
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new user"""
        user_data = api.payload

        # Simulate email uniqueness check
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        # We explicitly omit the password from the response
        return {'id': new_user.id, 'first_name': new_user.first_name, 'last_name': new_user.last_name, 'email': new_user.email}, 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of all users"""
        users = facade.get_all_users()
        # We explicitly omit the password from the response
        return [{'id': u.id, 'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email} for u in users], 200

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        # We explicitly omit the password from the response
        return {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}, 200

    @api.expect(user_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    def put(self, user_id):
        """Update user details"""
        user_data = api.payload
        updated_user = facade.update_user(user_id, user_data)
        
        if not updated_user:
            return {'error': 'User not found'}, 404
            
        # We explicitly omit the password from the response
        return {'id': updated_user.id, 'first_name': updated_user.first_name, 'last_name': updated_user.last_name, 'email': updated_user.email}, 200
```
### 3. Registrar el Namespace (`app/__init__.py`)
Agregar las rutas al archivo principal

### 4.

### 5. El viaje completo del Error:
Cuando dejas el nombre vacío en Swagger, pasa esto:

1.   Swagger (API): Toma el JSON y se lo da a `users.py`.
2.   `users.py` (Presentación): Le dice a la Fachada: "Crea este usuario".
3.   `facade.py` (Negocio): Revisa el email. Todo bien. Luego intenta construir el objeto: `User(**user_data)`.
4.   `user.py` (Modelo): Revisa el diccionario, ve que `first_name` está vacío y explota lanzando `ValueError("Invalid first_name")`.
5.   El rebote: El error rebota hacia arriba, sale del Modelo, atraviesa la Fachada y llega al `try/except` que acabamos de poner en `users.py`.
6.   La captura: `users.py` atrapa el error, extrae el texto (`str(e)`) que el Modelo gritó, y se lo devuelve a Swagger como un bonito JSON 400. 
### Outcome


---
---

