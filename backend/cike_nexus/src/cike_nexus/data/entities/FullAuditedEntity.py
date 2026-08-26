from datetime import datetime,timezone
from abc import ABC
from sqlmodel import Field, SQLModel
from sqlalchemy import BigInteger


class FullAuditedEntity(SQLModel, ABC):
    id: int | None = Field(default=None, primary_key=True, sa_type=BigInteger)
    create_at: datetime = Field(default=datetime.now(timezone.utc), index=True)
    update_at: datetime
    created_by: int | None = Field(default=None, sa_type=BigInteger, index=True)
    updated_by: int | None = Field(default=None, sa_type=BigInteger, index=True)
    is_deleted: bool = Field(default=False, index=True)
