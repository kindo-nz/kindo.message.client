# Kindo Python Client

A Python SDK for sending structured messages to the Kindo Producer Lambda service via Function URL with AWS SigV4 authentication.

## Features

- **AWS SigV4 Authentication**: Secure message transmission using AWS credentials
- **JSON Schema Validation**: Built-in message structure validation
- **Type Safety**: Full type hints and TypedDict support
- **Environment Configuration**: Flexible configuration via environment variables
- **Error Handling**: Comprehensive error handling with meaningful messages

## Installation

### Prerequisites

- Python 3.8+
- AWS credentials configured (via AWS CLI, IAM role, or environment variables)
- Access to Kindo Producer Lambda Function URL

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required
KINDO_MESSAGE_PRODUCER_URL=https://your-lambda-function-url.amazonaws.com
KINDO_MESSAGE_BEHAVIOR=instant

# Optional (defaults shown)
AWS_REGION=ap-southeast-2
AWS_SERVICE=lambda
```

### AWS Credentials

Ensure your AWS credentials are properly configured using one of these methods:

1. **AWS CLI**: `aws configure`
2. **Environment Variables**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. **IAM Role**: If running on AWS infrastructure
4. **AWS Credentials File**: `~/.aws/credentials`

## Usage

### Basic Example

```python
from kindo_message_client.producer import send_to_producer

# Message structure
message = {
    "event_type": "user.notification",
    "message_channel": "email",
    "behavior": "instant",
    "payload": {
        "user_id": "12345",
        "subject": "Welcome to Kindo!",
        "content": "Thank you for joining our platform."
    }
}

# For sensitive data, specify security_level
sensitive_message = {
    "event_type": "payment.processed",
    "message_channel": "internal",
    "behavior": "instant",
    "security_level": "sensitive",  # Payload will be hashed for security
    "payload": {
        "user_id": "12345",
        "credit_card_last4": "1234",
        "amount": 99.99,
        "transaction_id": "txn_abc123"
    }
}

# Send message
try:
    tracking_id = send_to_producer(
        url="https://your-lambda-function-url.amazonaws.com",
        message=message
    )
    print(f"Message sent successfully. Tracking ID: {tracking_id}")
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"Send error: {e}")
```

### Advanced Example with Custom Configuration

```python
from kindo_message_client.producer import send_to_producer

# Custom configuration with sensitive data
message = {
    "event_type": "order.status_update",
    "message_channel": "sms",
    "behavior": "instant",
    "security_level": "sensitive",  # Protect sensitive order information
    "payload": {
        "order_id": "ORD-12345",
        "status": "shipped",
        "estimated_delivery": "2024-01-15",
        "customer_phone": "+1234567890",
        "shipping_address": "123 Main St, City, State"
    }
}

# Send with custom AWS region
tracking_id = send_to_producer(
    url="https://your-lambda-function-url.amazonaws.com",
    message=message,
    region="us-east-1"  # Override default region
)
```

## API Reference

### `send_to_producer`

Sends a structured message to the Kindo Producer Lambda.

#### Parameters

- `url` (str): The Lambda Function URL endpoint
- `message` (ProducerPayload): The message to send
- `region` (str, optional): AWS region (default: from environment or "ap-southeast-2")
- `service` (str, optional): AWS service name (default: from environment or "lambda")
- `schema_path` (str, optional): Path to JSON schema file (default: built-in schema)

#### Returns

- `str`: Tracking ID returned by the producer service

#### Raises

- `ValueError`: When message validation fails
- `RuntimeError`: When message sending fails
- `ConfigError`: When required environment variables are missing

### Message Structure

The `ProducerPayload` TypedDict defines the required message structure:

```python
class ProducerPayload(TypedDict):
    event_type: str          # Event type identifier
    message_channel: str     # Message delivery channel
    behavior: Literal["instant"]  # Message behavior (currently only "instant" supported)
    payload: dict            # Message content data
    security_level: NotRequired[Literal["sensitive", "normal"]]  # Optional security level
```

## Message Schema

Messages must conform to the JSON schema defined in `schemas/producer_payload.json`:

```json
{
  "event_type": "string",
  "message_channel": "string",
  "behavior": "instant",
  "security_level": "normal|sensitive",
  "payload": {}
}
```

### Security Levels

The optional `security_level` field controls data protection:

- **`"normal"`** (default): Payload stored as-is for full tracking visibility
- **`"sensitive"`**: Payload automatically hashed before storage to protect sensitive data

When `security_level` is not provided, it defaults to `"normal"`.

## Error Handling

The client provides comprehensive error handling:

```python
try:
    tracking_id = send_to_producer(url, message)
except ValueError as e:
    # Schema validation failed
    print(f"Invalid message format: {e}")
except RuntimeError as e:
    # HTTP request failed
    print(f"Failed to send message: {e}")
except Exception as e:
    # Other errors (configuration, network, etc.)
    print(f"Unexpected error: {e}")
```

## Testing

Run the test suite:

```bash
cd tests
pytest
```

## Examples

### Notification System

```python
from datetime import datetime
from kindo_message_client.producer import send_to_producer

def send_user_notification(user_id: str, message: str, channel: str, is_sensitive: bool = False):
    payload = {
        "event_type": "user.notification",
        "message_channel": channel,
        "behavior": "instant",
        "payload": {
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Add security level for sensitive notifications
    if is_sensitive:
        payload["security_level"] = "sensitive"
    
    return send_to_producer(PRODUCER_URL, payload)

# Example usage
send_user_notification("12345", "Your password has been reset", "email", is_sensitive=True)
```

### Event Logging

```python
from datetime import datetime
from kindo_message_client.producer import send_to_producer

def log_system_event(event_type: str, data: dict):
    payload = {
        "event_type": f"system.{event_type}",
        "message_channel": "logging",
        "behavior": "instant",
        "payload": {
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
    }
    
    return send_to_producer(PRODUCER_URL, payload)
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure AWS credentials are properly configured
   - Check environment variables or AWS credentials file

2. **Schema Validation Errors**
   - Verify message structure matches the required schema
   - Check that all required fields are present

3. **Network Errors**
   - Verify the Lambda Function URL is correct and accessible
   - Check network connectivity and firewall settings

4. **Configuration Errors**
   - Ensure all required environment variables are set
   - Verify the `.env` file is in the correct location

## Contributing

When contributing to the Python client:

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Include comprehensive tests
4. Update documentation for any API changes
5. Ensure compatibility with the shared message schema
