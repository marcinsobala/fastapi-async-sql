from abc import ABC, abstractmethod
from typing import (
    Any,
)

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from adapters.database import (
    TransferDb,
)
from exceptions import TransferAlreadyExists, ResourceDoesNotExist


class AbstractTransfersDAL(ABC):
    @abstractmethod
    def get_transfer(self, transfer_id: int):
        pass

    @abstractmethod
    def get_transfers(self, filters: dict[str, Any] | None = None):
        pass

    @abstractmethod
    def create_transfer(self, create_data: dict[str, Any]):
        pass

    @abstractmethod
    def update_transfer(self, transfer_id: int, update_data: dict[str, Any]):
        pass

    @abstractmethod
    def delete_transfer(self, transfer_id: int):
        pass


class TransfersDAL(AbstractTransfersDAL):
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def get_transfer(self, transfer_id: int):
        transfer = await self.session.get(TransferDb, transfer_id)
        if transfer is None:
            raise ResourceDoesNotExist(f"Currency with id: {transfer_id} not found")
        return transfer

    async def get_transfers(self, filters: dict[str, Any] | None = None):
        transfers = await self.session.execute(select(TransferDb).filter_by(**filters or {}))
        return transfers.scalars().all()

    async def create_transfer(self, create_data: dict[str, Any]):
        new_transfer = TransferDb(**create_data)
        try:
            self.session.add(new_transfer)
            await self.session.flush()
        except IntegrityError:
            raise ResourceDoesNotExist(f"Provided user and/or currency does not exist")
        return new_transfer

    async def update_transfer(self, transfer_id: int, update_data: dict[str, Any]):
        transfer = await self.get_transfer(transfer_id)
        try:
            for key, value in update_data.items():
                setattr(transfer, key, value)
            await self.session.flush()
        except IntegrityError:
            raise TransferAlreadyExists(f"Transfer with data: {update_data} already exists")

    async def delete_transfer(self, transfer_id: int):
        # forbid if transfer is used in transfer

        q = delete(TransferDb).where(TransferDb.id == transfer_id)
        delete_operation = await self.session.execute(q)
        if delete_operation.rowcount is 0:
            raise ResourceDoesNotExist(f"User with id {transfer_id} not found")