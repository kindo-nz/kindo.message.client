import os
import pytest
from unittest.mock import patch, MagicMock
from .. import producer

PRODUCER_URL = os.getenv("KINDO_MESSAGE_PRODUCER_URL")  # inject this during testing


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