from typing import Annotated

from pydantic import BeforeValidator
from sqlalchemy import JSON
from sqlmodel import Field, Column

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity

class Knowledge(FullAuditedEntity, table=True):
    display_name: str = Field(default="", description="显示名称", index=True, nullable=False, max_length=256)
    name: str = Field(default="", description="名称", index=True, nullable=False, max_length=256)
    description: str = Field(default="", description="描述", index=True, nullable=False, max_length=512)
    avatar: str = Field(default="", description="头像地址", nullable=False, max_length=256)
    embedding_model:str = Field(max_length=128)
    collection_name:str = Field(max_length=256)
    vector_service_id:str = Field(max_length=256)

