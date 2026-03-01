#!/usr/bin/python3
# Es una librería de Python que genera identificadores únicos.
import uuid
# Librería para trabajar con fechas y horas. La usamos para registrar cuándo se creó o modificó un objeto.
from datetime import datetime

# Todo lo que creemos (usuarios, lugares, etc.) va a heredar de esta plantilla.
class BaseModel:
    def __init__(self):
        # uuid.uuid4() — Genera un ID único y aleatorio, como a3f8c2d1-.... 
        # El str() lo convierte a texto para poder guardarlo fácilmente.
        self.id = str(uuid.uuid4())
        # datetime.now() — Captura la fecha y hora exacta en este momento. Tanto
        self.created_at = datetime.now()
        # created_at como updated_at arrancan con el mismo valor.
        self.updated_at = datetime.now()
    # Cada vez que llamás a save(), actualiza updated_at con la hora actual. 
    # Es como un sello de "última modificación".
    def save(self):
        """
        Update the updated_at timestamp whenever the object is modified
        """
        self.updated_at = datetime.now()
    # data — Es un diccionario con los nuevos valores, por ejemplo {'first_name': 'Julian'}.
    def update(self, data):
        """
        Update the attributes of the object based on the provided dictionary
        """
        # data.items() — Recorre el diccionario entregando pares de key (nombre del campo) y value (valor nuevo).
        for key, value in data.items():
            # Antes de modificar algo, verifica que el objeto realmente tenga ese atributo. 
            # Si alguien intenta meter un campo que no existe, simplemente se ignora.
            if hasattr(self, key):
                #  Modifica el atributo dinámicamente. 
                # Es equivalente a escribir self.first_name = 'Julian' pero sin saber de antemano qué campo vas a cambiar.
                setattr(self, key, value)
        # Al terminar la actualización, registra automáticamente la hora del cambio.
        self.save()
    # pass — No hace nada por ahora. 
    # Es un espacio reservado para cuando en la Parte 3 necesitemos eliminar registros de la base de datos real.
    def delete(self):
        """Placeholder for delete operation (matches UML diagram)."""
        pass
    # Es el método que Python usa cuando imprimís un objeto en la terminal. 
    # En lugar de ver algo como <object at 0x7f3a...>, verás <User a3f8c2d1...>. Muy útil para depurar.
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
