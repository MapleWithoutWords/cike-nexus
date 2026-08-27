
from pydantic import BaseModel

from cike_nexus.data.enums.ToolType import ToolType


class ModelConfigValue(BaseModel):
    model:str
    temperature:float
    top_p:float
