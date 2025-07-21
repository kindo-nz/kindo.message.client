import os
from dotenv import load_dotenv

load_dotenv()

class ConfigError(Exception):
    pass

REQUIRED_ENV_VARS = [
    # "KINDO_MESSAGE_PRODUCER_URL",
    # "KINDO_MESSAGE_BEHAVIOR"
]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise ConfigError(f"Missing required environment variable: {var}")

KINDO_MESSAGE_PRODUCER_URL  = os.environ["KINDO_MESSAGE_PRODUCER_URL"] or ""
KINDO_MESSAGE_BEHAVIOR      = os.environ["KINDO_MESSAGE_BEHAVIOR"] or "instant"

AWS_REGION                  = os.environ.get("AWS_REGION", "ap-southeast-2")
AWS_SERVICE                 = os.environ.get("AWS_SERVICE", "lambda")

# Schema path relative to project root
SCHEMA_PATH = "../../schemas/producer_payload.json"
