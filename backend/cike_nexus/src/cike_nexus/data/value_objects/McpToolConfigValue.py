from abc import ABC

from cike_nexus.data.enums.McpType import McpType


class McpToolConfigValue(ABC):
    type:McpType

class StdioMcpToolConfigValue(McpToolConfigValue):
    command:str
    args:list[str]
    env:dict[str, str]


class HttpMcpToolConfigValue(McpToolConfigValue):
    url:str
    headers:dict[str, str]
    timeout:int