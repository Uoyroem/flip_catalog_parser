from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from ..products.models import Product


class Catalog(Base):
    __tablename__ = "catalogs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("catalogs.id"))

    parent: Mapped["Catalog"] = relationship(
        "Catalog", back_populates="children", remote_side=[id], lazy="selectin"
    )
    children: Mapped[list["Catalog"]] = relationship(
        "Catalog",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="catalog",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Catalog(id={self.id}, name='{self.name}')>"
