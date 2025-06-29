import json
import os
import jsonschema
from typing import Literal, TypedDict
from signer import signed_post
from config import AWS_REGION, AWS_SERVICE, SCHEMA_PATH

class ProducerPayload(TypedDict):
    event_type: str
    message_channel: str
    behavior: Literal["instant"]
    payload: dict

def send_to_producer(
    url: str,
    message: ProducerPayload,
    region: str = AWS_REGION,
    service: str = AWS_SERVICE,
    schema_path: str = SCHEMA_PATH
) -> str:
    with open(os.path.join(os.path.dirname(__file__), schema_path)) as f:
        schema = json.load(f)
    try:
        jsonschema.validate(instance=message, schema=schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"Invalid message structure: {e.message}")

    response = signed_post(url, message, region, service)
    if response.status_code == 200:
        return response.json().get("tracking_id")
    raise RuntimeError(f"Failed to send message: {response.status_code} {response.text}")