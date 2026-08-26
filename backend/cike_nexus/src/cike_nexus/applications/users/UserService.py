from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlmodel import Session,select

from cike_nexus.data import DbContext
from cike_nexus.data.entities.User import User
from cike_nexus.dtos.users.AddUserDto import AddUserDto
from cike_nexus.utilities.PasswordHasher import PasswordHasher


class UserService:
    def __init__(self, session:Annotated[DbContext,Depends(DbContext.get_session)])->int:
        self.session: Session = session

    def add(self,dto:AddUserDto):
        existing = self.session.exec(
            select(User).where(User.username == dto.username)
        ).first()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"username '{dto.username}' already exists",
            )

        user = User(
            name=dto.name,
            username=dto.username,
            password=PasswordHasher.hash(dto.password),
            avatar=dto.avatar,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user.id
