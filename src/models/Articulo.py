from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .objectid import PydanticObjectId

class Articulo(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    idUsuario: PydanticObjectId
    nombre: str
    imagen: str
    precio: int
    descripcion: str

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
