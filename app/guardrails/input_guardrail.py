
import re

from app.guardrails.policies import (
    BLOCK_MESSAGE,
    DEFAULT_ACTION
)


BLOCK_PATTERNS = {
    "violence": [
        r"\bhow\s+(?:can|do|to)\s+(?:i|we)\s+(?:kill|murder|poison)\b",
        r"\b(?:plan|commit|carry\s+out)\s+(?:a\s+)?(?:murder|assassination)\b",
        r"\b(?:kill|murder)\s+(?:someone|somebody|a\s+person|him|her)\b"
    ],

    "crime": [
        r"\bhow\s+(?:can|do|to)\s+(?:i|we)\s+(?:rob|steal|burgle)\b",
        r"\bhow\s+(?:can|do|to)\s+(?:i|we)\s+commit\s+fraud\b",
        r"\b(?:rob|steal)\s+(?:a\s+bank|money|someone)\b",
        r"\b(?:avoid|get\s+away\s+with)\s+(?:getting\s+)?caught\b"
    ],

    "cyber_abuse": [
        r"\bsteal\s+(?:someone'?s?\s+)?passwords?\b",
        r"\bhack\s+into\s+someone'?s?\s+account\b",
        r"\bdeploy\s+malware\s+to\s+steal\b",
        r"\bsteal\s+(?:login\s+)?credentials\b"
    ],

    "harassment": [
        r"\bhow\s+(?:can|do)\s+(?:i|we)\s+threaten\s+someone\b",
        r"\bhelp\s+me\s+intimidate\s+someone\b"
    ]
}


def check_user_input(user_message: str) -> dict:

    if not isinstance(user_message, str):
        return {
            "allowed": False,
            "category": "invalid_input",
            "message": "Invalid input format."
        }

    if not user_message.strip():
        return {
            "allowed": False,
            "category": "invalid_input",
            "message": "Please enter a valid question."
        }

    normalized_message = user_message.lower()

    for category, patterns in BLOCK_PATTERNS.items():

        for pattern in patterns:

            if re.search(pattern, normalized_message):

                return {
                    "allowed": False,
                    "category": category,
                    "message": BLOCK_MESSAGE
                }

    return {
        "allowed": DEFAULT_ACTION == "ALLOW",
        "category": "none",
        "message": "Input passed the initial rule-based check."
    }
