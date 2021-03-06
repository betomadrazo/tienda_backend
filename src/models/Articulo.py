import os
import base64
from PIL import Image
from io import BytesIO
from datetime import datetime

from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .objectid import PydanticObjectId
from .. import app

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

    def convert_base64_to_image(self, url_root):
        images_folder = 'articles_images'
        file_name = self.get_image_name()

        im = Image.open(BytesIO(base64.b64decode(self.imagen)))
        im.save(
            os.path.join(
                os.environ.get('STATIC_FOLDER'),
                images_folder,
                file_name)
            , 'PNG')
        self.imagen = "{}{}/{}/{}".format(
            url_root, 'static', images_folder, file_name)


def get_image_name(image_name):
    now = datetime.now()
    date_time = now.strftime("%m%d%y%H%M%S")

    return "{}_{}.png".format(
        image_name.lower().replace(' ', '_'), date_time)


def convert_base64_to_image(url_root, image, file_name):
    images_folder = 'articles_images'

    im = Image.open(BytesIO(base64.b64decode(image)))
    im.save(
        os.path.join(
            os.environ.get('STATIC_FOLDER'),
            images_folder,
            file_name)
        , 'PNG')
    return "{}{}/{}/{}".format(
        url_root, 'static', images_folder, file_name)
