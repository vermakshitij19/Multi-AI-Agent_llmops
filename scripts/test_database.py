
from app.evaluation.database import SessionLocal
from app.evaluation.crud import save_evaluation

# Sample evaluation data
sample_evaluation = {
    "relevance": {"score": 5, "reason": "Relevant answer"},
    "correctness": {"score": 5, "reason": "Technically correct"},
    "completeness": {"score": 4, "reason": "Could include more details"},
    "clarity": {"score": 5, "reason": "Easy to understand"},
    "overall_score": 4.75,
    "overall_feedback": "Good quality answer."
}

db = SessionLocal()

try:
    record = save_evaluation(
        db=db,
        question="What is Kubernetes?",
        answer="Kubernetes is a container orchestration platform.",
        evaluation=sample_evaluation
    )

    print("Evaluation saved successfully!")
    print("Evaluation ID:", record.id)
    print("Overall Score:", record.overall_score)

finally:
    db.close()
