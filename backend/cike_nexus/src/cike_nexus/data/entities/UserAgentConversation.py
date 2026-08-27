from sqlmodel import Field

from cike_nexus.data.abstracts.FullAuditedEntity import FullAuditedEntity
from sqlalchemy import BigInteger


class UserAgentConversation(FullAuditedEntity, table=True):
    conversation_id: int = Field(description="会话id", index=True, nullable=False, sa_type=BigInteger)
    user_id: int = Field(default="用户id", index=True, nullable=False, sa_type=BigInteger)
