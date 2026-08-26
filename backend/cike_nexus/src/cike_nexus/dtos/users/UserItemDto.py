from cike_nexus.dtos.FullAuditedDto import AuditedDto

class UserItemDto(AuditedDto):
    username: str
    password: str
    name: str
    avatar: str