import os
import json
import pytest
from unittest.mock import patch, MagicMock
from .. import producer

PRODUCER_URL = os.getenv("KINDO_MESSAGE_PRODUCER_URL")  # inject this during testing
PRODUCER_ARN = os.getenv("KINDO_MESSAGE_PRODUCER_ARN")  # inject this during testing

@pytest.fixture
def valid_message():
    return {
        "event_type": "hello.world",
        "message_channel": "test.client",
        "behavior": "instant",
        "payload": {"test_name": "integration test"}
    }

@pytest.fixture
def valid_message_with_security_level():
    return {
        "event_type": "hello.world",
        "message_channel": "test.client",
        "behavior": "instant",
        "payload": {"test_name": "integration test"},
        "security_level": "sensitive"
    }

def test_schema_validation_and_config_load(valid_message):
    # Remove a required field to force schema validation failure
    invalid_message = valid_message.copy()
    del invalid_message["event_type"]
    with pytest.raises(ValueError) as exc_info:
        producer.send_to_producer("http://fake-url.com", invalid_message)
    assert "'event_type' is a required property" in str(exc_info.value)

@patch.object(producer, 'signed_post')
def test_security_level_default_assignment(mock_signed_post, valid_message):
    """Test that security_level defaults to 'normal' when not provided"""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tracking_id": "test-123"}
    mock_signed_post.return_value = mock_response
    
    # Make a copy to avoid modifying the fixture
    message = valid_message.copy()
    
    # Ensure security_level is not in the message initially
    assert "security_level" not in message
    
    # Call the function with a test URL (mock will handle the actual request)
    test_url = PRODUCER_URL or "http://test-url.com"
    tracking_id = producer.send_to_producer(test_url, message)
    
    # Check that security_level was added with default value
    assert message["security_level"] == "normal"
    assert tracking_id == "test-123"
    
    # Verify the mock was called with the modified message
    mock_signed_post.assert_called_once()
    call_args = mock_signed_post.call_args[0]
    sent_message = call_args[1]
    assert sent_message["security_level"] == "normal"

@patch.object(producer, 'signed_post')
def test_security_level_preserved_when_provided(mock_signed_post, valid_message_with_security_level):
    """Test that provided security_level value is preserved"""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tracking_id": "test-456"}
    mock_signed_post.return_value = mock_response
    
    # Make a copy to avoid modifying the fixture
    message = valid_message_with_security_level.copy()
    
    # Ensure security_level is set to "sensitive" initially
    assert message["security_level"] == "sensitive"
    
    # Call the function with a test URL (mock will handle the actual request)
    test_url = PRODUCER_URL or "http://test-url.com"
    tracking_id = producer.send_to_producer(test_url, message)
    
    # Check that security_level was preserved
    assert message["security_level"] == "sensitive"
    assert tracking_id == "test-456"
    
    # Verify the mock was called with the original message
    mock_signed_post.assert_called_once()
    call_args = mock_signed_post.call_args[0]
    sent_message = call_args[1]
    assert sent_message["security_level"] == "sensitive"

def test_invalid_security_level_validation():
    """Test that invalid security_level values are rejected by schema validation"""
    invalid_message = {
        "event_type": "hello.world",
        "message_channel": "test.client",
        "behavior": "instant",
        "payload": {"test_name": "integration test"},
        "security_level": "invalid_value"
    }
    
    with pytest.raises(ValueError) as exc_info:
        producer.send_to_producer("http://fake-url.com", invalid_message)
    assert "Invalid message structure" in str(exc_info.value)

@pytest.mark.skipif(PRODUCER_URL is None, reason="KINDO_MESSAGE_PRODUCER_URL not set")
def test_signed_post_success(valid_message):
    tracking_id = producer.send_to_producer(PRODUCER_URL, valid_message)
    assert isinstance(tracking_id, str) and len(tracking_id) > 0

@pytest.mark.skipif(PRODUCER_URL is None, reason="KINDO_MESSAGE_PRODUCER_URL not set")
def test_signed_post_success_with_security_level(valid_message_with_security_level):
    """Integration test with security_level field"""
    tracking_id = producer.send_to_producer(PRODUCER_URL, valid_message_with_security_level)
    assert isinstance(tracking_id, str) and len(tracking_id) > 0


# Tests for send_to_producer_via_arn
def test_arn_schema_validation(valid_message):
    """Test that ARN function validates message schema the same way as URL function"""
    # Remove a required field to force schema validation failure
    invalid_message = valid_message.copy()
    del invalid_message["event_type"]
    with pytest.raises(ValueError) as exc_info:
        producer.send_to_producer_via_arn("arn:aws:lambda:us-east-1:123456789012:function:test-function", invalid_message)
    assert "'event_type' is a required property" in str(exc_info.value)


@patch('boto3.client')
def test_arn_lambda_invocation_success(mock_boto3_client, valid_message):
    """Test successful Lambda invocation via ARN with mocked boto3"""
    # Mock the Lambda client and its invoke method
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    
    # Mock successful response with direct Lambda format
    mock_response = {
        'StatusCode': 200,
        'Payload': MagicMock()
    }
    mock_response['Payload'].read.return_value = json.dumps({"tracking_id": "test-tracking-123"}).encode()
    mock_lambda_client.invoke.return_value = mock_response
    
    # Call the function
    arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    tracking_id = producer.send_to_producer_via_arn(arn, valid_message)
    
    # Verify the result
    assert tracking_id == "test-tracking-123"
    
    # Verify boto3 client was called correctly
    mock_boto3_client.assert_called_once_with('lambda', region_name='ap-southeast-2')
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=arn,
        InvocationType='RequestResponse',
        Payload=json.dumps(valid_message)
    )


@patch('boto3.client')
def test_arn_lambda_invocation_api_gateway_response(mock_boto3_client, valid_message):
    """Test successful Lambda invocation with API Gateway response format"""
    # Mock the Lambda client and its invoke method
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    
    # Mock successful response with API Gateway format
    api_gateway_response = {
        'statusCode': 200,
        'body': json.dumps({"tracking_id": "api-gateway-tracking-456"})
    }
    mock_response = {
        'StatusCode': 200,
        'Payload': MagicMock()
    }
    mock_response['Payload'].read.return_value = json.dumps(api_gateway_response).encode()
    mock_lambda_client.invoke.return_value = mock_response
    
    # Call the function
    arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    tracking_id = producer.send_to_producer_via_arn(arn, valid_message)
    
    # Verify the result
    assert tracking_id == "api-gateway-tracking-456"


@patch('boto3.client')
def test_arn_lambda_invocation_failure(mock_boto3_client, valid_message):
    """Test Lambda invocation failure handling"""
    # Mock the Lambda client and its invoke method
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    
    # Mock failed response
    mock_response = {
        'StatusCode': 500,
        'Payload': MagicMock()
    }
    mock_response['Payload'].read.return_value = json.dumps({"errorMessage": "Internal error"}).encode()
    mock_lambda_client.invoke.return_value = mock_response
    
    # Call the function and expect RuntimeError
    arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    with pytest.raises(RuntimeError) as exc_info:
        producer.send_to_producer_via_arn(arn, valid_message)
    
    assert "Lambda invocation failed with status: 500" in str(exc_info.value)


@patch('boto3.client')
def test_arn_lambda_api_gateway_error_response(mock_boto3_client, valid_message):
    """Test API Gateway error response handling"""
    # Mock the Lambda client and its invoke method
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    
    # Mock API Gateway error response
    api_gateway_error = {
        'statusCode': 400,
        'body': json.dumps({"error": "Bad Request"})
    }
    mock_response = {
        'StatusCode': 200,
        'Payload': MagicMock()
    }
    mock_response['Payload'].read.return_value = json.dumps(api_gateway_error).encode()
    mock_lambda_client.invoke.return_value = mock_response
    
    # Call the function and expect RuntimeError
    arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    with pytest.raises(RuntimeError) as exc_info:
        producer.send_to_producer_via_arn(arn, valid_message)
    
    assert "Failed to send message: 400" in str(exc_info.value)


@patch('boto3.client')
def test_arn_boto3_exception_handling(mock_boto3_client, valid_message):
    """Test boto3 exception handling"""
    # Mock the Lambda client to raise an exception
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.side_effect = Exception("AWS credentials not found")
    
    # Call the function and expect RuntimeError
    arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    with pytest.raises(RuntimeError) as exc_info:
        producer.send_to_producer_via_arn(arn, valid_message)
    
    assert "Failed to invoke Lambda function: AWS credentials not found" in str(exc_info.value)


@pytest.mark.skipif(PRODUCER_ARN is None, reason="KINDO_MESSAGE_PRODUCER_ARN not set")
def test_arn_integration_success(valid_message):
    """Integration test for ARN function with real AWS Lambda"""
    tracking_id = producer.send_to_producer_via_arn(PRODUCER_ARN, valid_message)
    assert isinstance(tracking_id, str) and len(tracking_id) > 0




