"""
Legal Query Result - armazenamento de consultas externas
"""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LegalQuery(Base):
    """Registro de consulta legal (DataJud, SIGEF, Conecta, etc)"""

    __tablename__ = "legal_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    query_type: Mapped[str] = mapped_column(String(100), nullable=False)
    query_params: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    investigation = relationship("Investigation", back_populates="legal_queries")
