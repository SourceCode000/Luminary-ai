import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import mapped_column, MappedColumn
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: MappedColumn[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: MappedColumn[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    hashed_password: MappedColumn[str] = mapped_column(
        String, nullable=False
    )
    is_active: MappedColumn[bool] = mapped_column(
        Boolean, default=True
    )