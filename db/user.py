import uuid
from enum import Enum

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum, String, BigInteger

from db.base import CreatedModel, db


class User(CreatedModel):
    class Role(Enum):
        ADMIN = 'Admin'
        USER = 'User'

    username: Mapped[str] = mapped_column(String)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="user_role"),
        default=Role.USER,
        nullable=False,
    )

    reports: Mapped[list["Report"]] = relationship(
        secondary=lambda: UserReportLink.__table__,
        back_populates="users",
    )

    @classmethod
    async def create_or_update(cls, **kwargs):
        async with db.session() as session:
            stmt = pg_insert(cls).values(**kwargs)
            stmt = stmt.on_conflict_do_update(
                index_elements=[cls.telegram_id],
                set_={"username": stmt.excluded.username, "role": stmt.excluded.role},
            ).returning(cls)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()


class Report(CreatedModel):
    class TypeCompany(Enum):
        ADLER = 'ADLER'
        GATTER = 'GATTER'

    type_company: Mapped[TypeCompany] = mapped_column(
        SQLEnum(TypeCompany, name="type_company"),
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        secondary=lambda: UserReportLink.__table__,
        back_populates="reports",
    )

    @classmethod
    async def create_report_for_user(cls, user_id, type_company):
        async with db.session() as session:
            report = Report(type_company=type_company)
            session.add(report)
            await session.flush()

            link = UserReportLink(user_id=user_id, report_id=report.id)
            session.add(link)

            await session.commit()
            return report


class UserReportLink(CreatedModel):
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    report_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reports.id"))

    __table_args__ = (
        UniqueConstraint("user_id", "report_id", name="uq_user_report"),
    )
