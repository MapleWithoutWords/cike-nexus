from abc import ABC

from pydantic import BaseModel

from cike_nexus.data.enums.ToolType import ToolType


class McpToolConfigValue(BaseModel,ABC):
    type:ToolType

class StdioMcpToolConfigValue(McpToolConfigValue):
    command:str
    args:list[str]
    env:dict[str, str]


class HttpMcpToolConfigValue(McpToolConfigValue):
    url:str
    headers:dict[str, str]
    timeout:int