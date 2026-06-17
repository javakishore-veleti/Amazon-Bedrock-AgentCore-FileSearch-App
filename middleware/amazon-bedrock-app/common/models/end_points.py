from pydantic import BaseModel


class EndPointDef(BaseModel):
    name: str
    end_point_type: str
