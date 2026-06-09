from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkflowLog(Base):
    __tablename__ = "workflow_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    paper_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    request_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
