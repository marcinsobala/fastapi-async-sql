from abc import ABC, abstractmethod
from typing import (
    Any,
)

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from adapters.database import UserDb
from exceptions import UserAlreadyExists, ResourceDoesNotExist


class AbstractUsersDAL(ABC):
    @abstractmethod
    def get_user(self, user_id: int):
        pass

    @abstractmethod
    def get_users(self, filters: dict[str, Any] | None = None):
        pass

    @abstractmethod
    def create_user(self, create_data: dict[str, Any]):
        pass

    @abstractmethod
    def update_user(self, user_id: int, update_data: dict[str, Any]):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass


class UsersDAL(AbstractUsersDAL):
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def get_user(self, user_id: int):
        user = await self.session.get(UserDb, user_id)
        if user is None:
            raise ResourceDoesNotExist(f"User with id {user_id} not found")
        return user

    async def get_users(self, filters: dict[str, Any] | None = None):
        users = await self.session.execute(select(UserDb).filter_by(**filters or {}))
        return users.scalars().all()

    async def create_user(self, create_data: dict[str, Any]):
        new_user = UserDb(**create_data)
        try:
            self.session.add(new_user)
            await self.session.flush()
        except IntegrityError:
            raise UserAlreadyExists(f"User with email: {new_user.email} already exists!")
        return new_user

    async def update_user(self, user_id: int, update_data: dict[str, Any]):
        user = await self.get_user(user_id)
        try:
            for key, value in update_data.items():
                setattr(user, key, value)
            await self.session.flush()
        except IntegrityError:
            raise UserAlreadyExists(f"User with following data: {update_data} already exists!")

    async def delete_user(self, user_id: int):
        q = delete(UserDb).where(UserDb.id == user_id)
        delete_operation = await self.session.execute(q)
        if delete_operation.rowcount is 0:
            raise ResourceDoesNotExist(f"User with id {user_id} not found")