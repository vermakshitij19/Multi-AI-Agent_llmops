
from pathlib import Path
from typing import List
from app.evaluation.crud import save_evaluation, get_all_evaluations
from app.evaluation.schemas import EvaluationResponse

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --------------------------------------------------
# Load environment variables BEFORE importing AI Agent
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=False)

# --------------------------------------------------
# Application imports
# --------------------------------------------------

from app.core.ai_agent import get_response_from_ai_agents
from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.guardrails.input_guardrail import check_user_input
from app.guardrails.output_guardrail import check_ai_output

from app.evaluation.llm_judge import evaluate_response
from app.evaluation.database import SessionLocal
from app.evaluation.crud import save_evaluation

# --------------------------------------------------
# Logger and FastAPI initialization
# --------------------------------------------------

logger = get_logger(__name__)

app = FastAPI(title="MULTI AI AGENT")



# --------------------------------------------------
# Request Model
# --------------------------------------------------

class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]
    allow_search: bool = False
    evaluate_response: bool = False


# --------------------------------------------------
# Health Check Endpoint
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Multi AI Agent backend is running"
    }

# --------------------------------------------------
# GET ALL EVALUATION HISTORY
# --------------------------------------------------

@app.get(
    "/evaluations",
    response_model=List[EvaluationResponse]
)
def get_evaluations():

    db = SessionLocal()

    try:
        logger.info("Fetching evaluation history")

        evaluations = get_all_evaluations(db)

        logger.info(
            "Retrieved %s evaluation records",
            len(evaluations)
        )

        return evaluations

    except Exception as e:

        logger.exception("Failed to retrieve evaluation history")

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve evaluation history"
        )

    finally:
        db.close()


# --------------------------------------------------
# Chat Endpoint
# --------------------------------------------------

@app.post("/chat")
def chat_endpoint(request: RequestState):

    logger.info(
        "Received request for model: %s",
        request.model_name
    )

    # --------------------------------------------------
    # Validate model
    # --------------------------------------------------

    if request.model_name not in settings.ALLOWED_MODEL_NAMES:

        logger.warning("Invalid model name received")

        raise HTTPException(
            status_code=400,
            detail="Invalid model name"
        )

    # --------------------------------------------------
    # Validate user query
    # --------------------------------------------------

    if not request.messages or not any(
        message.strip() for message in request.messages
    ):

        raise HTTPException(
            status_code=400,
            detail="Please provide a valid user query"
        )

    # --------------------------------------------------
    # INPUT GUARDRAIL CHECK
    # --------------------------------------------------

    for message in request.messages:

        guardrail_result = check_user_input(message)

        if not guardrail_result["allowed"]:

            logger.warning(
                "Input blocked by guardrail. Category: %s",
                guardrail_result["category"]
            )

            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Request blocked by Input Guardrail",
                    "category": guardrail_result["category"],
                    "message": guardrail_result["message"]
                }
            )

    # --------------------------------------------------
    # Validate Tavily API key
    # --------------------------------------------------

    if request.allow_search:

        if not settings.TAVILY_API_KEY:

            logger.error("TAVILY_API_KEY not found")

            raise HTTPException(
                status_code=400,
                detail=(
                    "Web search requires TAVILY_API_KEY. "
                    "Please check your .env file."
                )
            )

    # --------------------------------------------------
    # Generate AI response
    # --------------------------------------------------

    try:

        logger.info("Generating AI response")

        response = get_response_from_ai_agents(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt
        )

        logger.info(
            "Successfully received response from AI Agent: %s",
            request.model_name
        )

        # --------------------------------------------------
        # OUTPUT GUARDRAIL CHECK
        # --------------------------------------------------

        output_result = check_ai_output(response)

        if not output_result["allowed"]:

            logger.warning(
                "Output blocked by guardrail. Category: %s",
                output_result["category"]
            )

            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Response blocked by Output Guardrail",
                    "category": output_result["category"],
                    "message": output_result["message"]
                }
            )

        safe_response = output_result["safe_output"]

        logger.info("Output passed Output Guardrails")

        # --------------------------------------------------
        # LLM-AS-A-JUDGE EVALUATION
        # --------------------------------------------------

        evaluation = None

        if request.evaluate_response:

            question = "\n".join(request.messages)

            logger.info("Starting LLM Judge evaluation")

            evaluation = evaluate_response(
                question=question,
                answer=safe_response
            )

            logger.info(
                "LLM Judge evaluation completed. Score: %s",
                evaluation["overall_score"]
            )

            # --------------------------------------------------
            # SAVE EVALUATION INTO SQLITE
            # --------------------------------------------------

            db = SessionLocal()

            try:

                record = save_evaluation(
                    db=db,
                    question=question,
                    answer=safe_response,
                    evaluation=evaluation
                )

                logger.info(
                    "Evaluation saved successfully. ID: %s",
                    record.id
                )

            except Exception:

                db.rollback()

                # Database failure should not block AI response
                logger.exception(
                    "Failed to save evaluation into database"
                )

            finally:
                db.close()

        # --------------------------------------------------
        # RETURN RESPONSE AND EVALUATION
        # --------------------------------------------------

        return {
            "response": safe_response,
            "evaluation": evaluation
        }

    except HTTPException:
        # Preserve intentional HTTP errors
        raise

    except Exception as e:

        logger.exception(
            "Error occurred during AI response generation or evaluation"
        )

        raise HTTPException(
            status_code=500,
            detail=str(
                CustomException(
                    "Failed to get AI response or evaluate it",
                    error_detail=e
                )
            )
        )
