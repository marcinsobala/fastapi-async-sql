import config
from sqlalchemy import (
    DECIMAL,
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.ext.declarative import (
    DeclarativeMeta,
    declarative_base,
)
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base: DeclarativeMeta = declarative_base()


class UserDb(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(), nullable=False)
    email = Column(String(), nullable=False, unique=True)
    surname = Column(String(), nullable=False)
    premium = Column(Boolean(), nullable=False, default=False)


class TransferDb(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, nullable=False)
    amount = Column(DECIMAL(), nullable=False)
    title = Column(String(length=85), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.id"))
    user_id = Column(Integer, ForeignKey("users.id"))


class CurrencyDb(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(length=30), nullable=False)
    acronym = Column(String(length=3), nullable=False, unique=True)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
