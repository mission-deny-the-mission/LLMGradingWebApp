from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class Work(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str]
    title: Mapped[str]
    author: Mapped[str]
    grade: Mapped[Optional[str]]
    status: Mapped[str]
    processed: Mapped[bool]