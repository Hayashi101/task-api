from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    price: Mapped[float] = mapped_column(Float, nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
