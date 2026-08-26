from sqlmodel import Field, SQLModel

from cike_nexus.data.entities.FullAuditedEntity import FullAuditedEntity


class AgentApplication(FullAuditedEntity, table=True):
    display_name:str= Field(default="", description="显示名称", index=True, nullable=False, max_length=256)
    name: str = Field(default="", description="名称", index=True, nullable=False, max_length=256)
    description: str = Field(default="", description="描述", index=True, nullable=False, max_length=512)
    avatar: str = Field(default="", description="头像地址", nullable=False, max_length=256)
    instructions: str = Field(default="", description="提示词", nullable=False)
    default_model:str = Field(default="", description="默认模型", nullable=False, max_length=256)
