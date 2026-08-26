from pydantic import BaseModel,Field


class AddUserDto(BaseModel):
    username: str = Field(description="用户名",  max_length=256)
    password: str = Field(description="密码", max_length=512)
    name: str = Field(description="名称", max_length=256)
    avatar: str = Field(default="头像地址", max_length=256)
