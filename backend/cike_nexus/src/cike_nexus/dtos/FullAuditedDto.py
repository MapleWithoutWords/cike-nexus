from pydantic import field_serializer
from datetime import datetime,timezone


class AuditedDto:
    id:int
    create_at: datetime
    update_at: datetime
    created_by: int | None
    updated_by: int | None

    @field_serializer("id")
    def serialize_id(self, value: int) -> str:
        return str(value)

class FullAuditedDto(AuditedDto):
    is_deleted: bool

