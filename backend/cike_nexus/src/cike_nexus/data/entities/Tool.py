from typing import Annotated, Union

from sqlalchemy import JSON
from sqlmodel import Field, Column

from cike_nexus.data.entities.FullAuditedEntity import FullAuditedEntity
from cike_nexus.data.enums.ToolType import ToolType
from cike_nexus.data.value_objects.McpToolConfigValue import StdioMcpToolConfigValue, HttpMcpToolConfigValue

ConfigType = Annotated[Union[StdioMcpToolConfigValue, HttpMcpToolConfigValue], Field(discriminator="type")]


class AgentApplication(FullAuditedEntity, table=True):
    name: str = Field(default="", description="名称", index=True, nullable=False, max_length=256)
    description: str = Field(default="", description="描述", index=True, nullable=False, max_length=512)
    type: ToolType = Field(default="", description="类型", index=True, nullable=False, max_length=512)
    disabled: bool = Field(default=False, description="类型", index=True, nullable=False, max_length=512)
    config: ConfigType = Field(sa_column=Column(JSON))
