from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QARecord(Base):
    __tablename__ = "qa_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("paper.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    paper = relationship("Paper", back_populates="qa_records")
