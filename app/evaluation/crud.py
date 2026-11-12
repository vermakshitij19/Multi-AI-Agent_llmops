
from sqlalchemy.orm import Session

from app.evaluation.models import EvaluationHistory


# --------------------------------------------------
# SAVE EVALUATION
# --------------------------------------------------

def save_evaluation(
    db: Session,
    question: str,
    answer: str,
    evaluation: dict
):
    """Save one LLM Judge evaluation into SQLite."""

    record = EvaluationHistory(
        question=question,
        answer=answer,
        relevance=evaluation["relevance"]["score"],
        correctness=evaluation["correctness"]["score"],
        completeness=evaluation["completeness"]["score"],
        clarity=evaluation["clarity"]["score"],
        overall_score=evaluation["overall_score"],
        feedback=evaluation["overall_feedback"]
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    except Exception:
        db.rollback()
        raise


# --------------------------------------------------
# GET ALL EVALUATIONS
# --------------------------------------------------

def get_all_evaluations(db: Session):
    """Retrieve all evaluation records from database."""

    return (
        db.query(EvaluationHistory)
        .order_by(EvaluationHistory.id.desc())
        .all()
    )
