from typing import Annotated

from fastapi import APIRouter, Depends

from cike_nexus.applications.users import UserService
from cike_nexus.dtos.users.AddUserDto import AddUserDto
from cike_nexus.dtos.users.UserItemDto import UserItemDto

router = APIRouter()

@router.post("")
def add(dto:AddUserDto,userService:Annotated[UserService,Depends(UserService)])->int:
   return userService.add(dto)

@router.get("")
def get(id:int)->UserItemDto:
    return UserItemDto()

