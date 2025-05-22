from pydantic import BaseModel as PydanticBaseModel


class BaseSchema(PydanticBaseModel):

    class Config:
        arbitrary_types_allowed = True
