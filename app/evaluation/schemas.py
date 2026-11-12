
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EvaluationResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    answer: str

    relevance: float
    correctness: float
    completeness: float
    clarity: float

    overall_score: float
    feedback: str | None = None

    created_at: datetime
