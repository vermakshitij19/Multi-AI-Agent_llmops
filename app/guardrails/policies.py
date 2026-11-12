GUARDRAIL_POLICIES = {
    "violence": {
        "description": "Requests to plan or facilitate physical violence.",
        "action": "BLOCK"
    },
    "crime": {
        "description": "Requests to facilitate theft, robbery, fraud or other crimes.",
        "action": "BLOCK"
    },
    "cyber_abuse": {
        "description": "Requests to steal credentials, compromise accounts or deploy malware.",
        "action": "BLOCK"
    },
    "harassment": {
        "description": "Requests to threaten, intimidate or target individuals.",
        "action": "BLOCK"
    },
    "educational": {
        "description": "Legitimate educational, research, historical and prevention questions.",
        "action": "ALLOW"
    }
}

DEFAULT_ACTION = "ALLOW"

BLOCK_MESSAGE = (
    "Your request cannot be processed because it appears to request "
    "assistance that could facilitate harm or illegal activity. "
    "Please ask about prevention, safety or educational information instead."
)
