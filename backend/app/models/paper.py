from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Paper(Base):
    __tablename__ = "paper"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    year: Mapped[str | None] = mapped_column(String(32), nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    method: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics: Mapped[str | None] = mapped_column(Text, nullable=True)
    contribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    limitation: Mapped[str | None] = mapped_column(Text, nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    qa_records = relationship(
        "QARecord",
        back_populates="paper",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    notes = relationship(
        "PaperNote",
        back_populates="paper",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
