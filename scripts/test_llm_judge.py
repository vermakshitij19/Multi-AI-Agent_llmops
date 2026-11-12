
from app.evaluation.llm_judge import evaluate_response


question = "What is Kubernetes?"

answer = """
Kubernetes is an open-source container orchestration platform.
It helps automate deployment, scaling and management
of containerized applications.
"""

print("Question:", question)
print("\nAI Answer:", answer)

result = evaluate_response(
    question=question,
    answer=answer
)

print("\n========== LLM EVALUATION ==========")

for metric in [
    "relevance",
    "correctness",
    "completeness",
    "clarity"
]:
    print(f"\n{metric.upper()}")
    print("Score:", result[metric]["score"])
    print("Reason:", result[metric]["reason"])

print("\nOVERALL SCORE:", result["overall_score"])
print("FEEDBACK:", result["overall_feedback"])
