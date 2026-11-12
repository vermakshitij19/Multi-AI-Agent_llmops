
import re


# Patterns for detecting sensitive information in AI responses
SENSITIVE_PATTERNS = {
    "groq_api_key": r"\bgsk_[A-Za-z0-9]{20,}\b",
    "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
    "github_token": r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
    "slack_token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
    "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "password_exposure": (
        r"(?i)\b(?:password|passwd)\s*[:=]\s*['\"]?"
        r"(?!\s*(?:your_password|example|placeholder))"
        r"[A-Za-z0-9!@#$%^&*_-]{8,}"
    )
}


# Patterns for detecting clearly harmful operational instructions
HARMFUL_OUTPUT_PATTERNS = {
    "credential_theft": [
        r"\bstep\s+\d+.*(?:steal|harvest).{0,40}password",
        r"\b(?:steal|harvest)\s+(?:someone'?s?\s+)?credentials"
    ],
    "malware": [
        r"\b(?:deploy|install)\s+malware\s+to\s+(?:steal|damage)",
        r"\bsteps?\s+to\s+(?:create|deploy)\s+ransomware"
    ],
    "violent_instructions": [
        r"\bstep\s+\d+.*\b(?:kill|murder)\s+(?:someone|a person)",
        r"\binstructions\s+to\s+(?:kill|murder)\s+someone"
    ]
}


BLOCKED_OUTPUT_MESSAGE = (
    "The AI-generated response was blocked by Output Guardrails "
    "because it may contain unsafe instructions or sensitive information."
)


def check_ai_output(ai_response: str) -> dict:
    """
    Check AI-generated output for sensitive information
    and clearly harmful operational instructions.
    """

    if not isinstance(ai_response, str):
        return {
            "allowed": False,
            "category": "invalid_output",
            "message": "Invalid AI response format.",
            "safe_output": None
        }

    if not ai_response.strip():
        return {
            "allowed": False,
            "category": "empty_output",
            "message": "The AI agent returned an empty response.",
            "safe_output": None
        }

    # Check for sensitive information
    for category, pattern in SENSITIVE_PATTERNS.items():
        if re.search(pattern, ai_response):
            return {
                "allowed": False,
                "category": category,
                "message": BLOCKED_OUTPUT_MESSAGE,
                "safe_output": None
            }

    # Check for harmful operational instructions
    for category, patterns in HARMFUL_OUTPUT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, ai_response, re.IGNORECASE | re.DOTALL):
                return {
                    "allowed": False,
                    "category": category,
                    "message": BLOCKED_OUTPUT_MESSAGE,
                    "safe_output": None
                }

    return {
        "allowed": True,
        "category": "none",
        "message": "Output passed the guardrail checks.",
        "safe_output": ai_response
    }
