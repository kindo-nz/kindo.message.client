import json
import os
import jsonschema
from typing import Literal, TypedDict, NotRequired
import boto3
from .signer import signed_post
from .config import AWS_REGION, AWS_SERVICE, SCHEMA_PATH

class ProducerPayload(TypedDict):
    event_type: str
    message_channel: str
    behavior: Literal["instant"]
    payload: dict
    security_level: NotRequired[Literal["sensitive", "normal"]]

def validate_message_with_schema(message: ProducerPayload) -> None:
    # Set default security_level if not provided
    if "security_level" not in message:
        message["security_level"] = "normal"
    # Load schema from package resources or local file
    try:
        # First try to load from package-local schemas (for installed package)
        schema_path = os.path.join(os.path.dirname(__file__), 'schemas/producer_payload.json')
        with open(schema_path) as f:
            schema = json.load(f)
    except Exception:
        # Fallback to project root schemas (for development)
        schema_path = os.path.join(os.path.dirname(__file__), SCHEMA_PATH)
        with open(schema_path) as f:
            schema = json.load(f)
    
    try:
        jsonschema.validate(instance=message, schema=schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"Invalid message structure: {e.message}")

def send_to_producer(
    url: str,
    message: ProducerPayload,
    region: str = AWS_REGION,
    service: str = AWS_SERVICE
) -> str:
    validate_message_with_schema(message)

    response = signed_post(url, message, region, service)
    if response.status_code == 200:
        return response.json().get("tracking_id")
    raise RuntimeError(f"Failed to send message: {response.status_code} {response.text}")


def send_to_producer_via_arn(
    arn: str,
    message: ProducerPayload,
    region: str = AWS_REGION,
) -> str:
    validate_message_with_schema(message)

    # Use boto3 to invoke Lambda function directly via ARN
    lambda_client = boto3.client('lambda', region_name=region)
    
    try:
        response = lambda_client.invoke(
            FunctionName=arn,
            InvocationType='RequestResponse',
            Payload=json.dumps(message)
        )
        
        # Read the response payload
        response_payload = json.loads(response['Payload'].read())
        
        # Check if the Lambda function executed successfully
        if response['StatusCode'] == 200:
            # Handle both direct response and API Gateway response formats
            if isinstance(response_payload, dict):
                if 'statusCode' in response_payload:
                    # API Gateway response format
                    if response_payload['statusCode'] == 200:
                        body = json.loads(response_payload['body']) if isinstance(response_payload['body'], str) else response_payload['body']
                        return body.get("tracking_id")
                    else:
                        raise RuntimeError(f"Failed to send message: {response_payload['statusCode']} {response_payload.get('body', '')}")
                else:
                    # Direct Lambda response format
                    return response_payload.get("tracking_id")
            else:
                raise RuntimeError(f"Unexpected response format: {response_payload}")
        else:
            raise RuntimeError(f"Lambda invocation failed with status: {response['StatusCode']}")
            
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise
        raise RuntimeError(f"Failed to invoke Lambda function: {str(e)}")