from sqlmodel import Field, SQLModel

from cike_nexus.data.entities.FullAuditedEntity import FullAuditedEntity


class User(FullAuditedEntity, table=True):
    username: str = Field(description="用户名", index=True, nullable=False, max_length=256)
    password: str = Field(description="密码", index=True, nullable=False, max_length=512)
    name: str = Field(description="名称", index=True, nullable=False, max_length=256)
    avatar: str = Field(default="头像地址", nullable=False, max_length=256)
