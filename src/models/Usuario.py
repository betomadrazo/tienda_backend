from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

import bcrypt

from .objectid import PydanticObjectId

class Usuario(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    nombre: str
    correo: Optional[str] = None
    contraseña: str

    def username_is_valid(self):
        return self.nombre.isalnum()

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

    def check_password(self, hashed_password):
        """Compare the provided password against the hashed password.
        """
        provided_password = self.contraseña.encode('utf-8')
        hashed_password = hashed_password.encode('utf-8')

        if bcrypt.checkpw(hashed_password, provided_password):
            return True
        return False

    def create_hashed_password(self):
        """Encrypt password before storing it in the database.
        """
        password = self.contraseña.encode('utf-8')
        salt = bcrypt.gensalt(rounds=10)
        self.contraseña = bcrypt.hashpw(password, salt)
