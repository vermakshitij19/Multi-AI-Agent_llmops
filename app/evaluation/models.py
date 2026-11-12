
from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from sqlalchemy.sql import func

from app.evaluation.database import Base


class EvaluationHistory(Base):
    __tablename__ = "evaluation_history"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    relevance = Column(Float, nullable=False)
    correctness = Column(Float, nullable=False)
    completeness = Column(Float, nullable=False)
    clarity = Column(Float, nullable=False)

    overall_score = Column(Float, nullable=False)

    feedback = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
