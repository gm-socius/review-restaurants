from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


class Owner(Base):
    __tablename__ = "owner_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email_address: Mapped[str]

    restaurants: Mapped[List["Restaurant"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Owner(id={self.id!r}, name={self.name!r}"


class Restaurant(Base):
    __tablename__ = "restaurant"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("owner_account.id"))

    owner: Mapped["Owner"] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Restaurant(id={self.id!r}, name={self.name!r}"
