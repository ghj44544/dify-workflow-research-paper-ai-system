from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaperNote(Base):
    __tablename__ = "paper_note"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("paper.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note_style: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    paper = relationship("Paper", back_populates="notes")
