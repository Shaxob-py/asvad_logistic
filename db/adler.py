from datetime import date as date_type
from enum import Enum

from sqlalchemy import select, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Enum as SQLEnum, String, BigInteger

from db.base import CreatedModel
from db.base import db


class TypeCompany(Enum):
    ADLER = 'ADLER'
    GATTER = 'GATTER'


class Entry(CreatedModel):
    region: Mapped[str] = mapped_column(String)
    date: Mapped[date_type] = mapped_column(Date)
    balance_before: Mapped[int] = mapped_column(BigInteger, nullable=True)
    inkassatsiya_amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=True)
    company: Mapped[TypeCompany] = mapped_column(SQLEnum(TypeCompany, name="company"), nullable=False)

    __table_args__ = (
        UniqueConstraint("region", "date", "company", name="uq_region_date_company"),
    )

    @classmethod
    async def select_months(cls, target_date) -> list:
        async with db.session() as session:
            query = select(cls).where(cls.date == target_date)
            res = await session.execute(query)
            return res.scalars().all()

    @classmethod
    async def create_or_update(cls, region: str, date, company: str, **kwargs):
        async with db.session() as session:
            stmt = pg_insert(cls).values(
                region=region, date=date, company=company, **kwargs
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["region", "date", "company"],
                set_=kwargs,
            )
            await session.execute(stmt)
            await session.commit()


class GroupEntry(CreatedModel):
    company: Mapped[TypeCompany] = mapped_column(SQLEnum(TypeCompany, name="company"), nullable=False)
    region: Mapped[str] = mapped_column(String)
    inkassatsiya_amount: Mapped[int] = mapped_column(BigInteger, nullable=True)
    date: Mapped[date_type] = mapped_column(Date)

    @classmethod
    async def get_by_region_date(cls, region, target_date, company):
        async with db.session() as session:
            query = select(cls).where(cls.region == region, cls.date == target_date, cls.company == company)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls):
        async with db.session() as session:
            query = select(cls)
            result = await session.execute(query)
            return result.scalars().all()

