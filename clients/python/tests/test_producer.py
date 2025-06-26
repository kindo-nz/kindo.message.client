import os
import pytest
from ..producer import send_to_producer

PRODUCER_URL = os.getenv("KINDO_MESSAGE_PRODUCER_URL")  # inject this during testing

@pytest.fixture
def valid_message():
    return {
        "event_type": "hello.world",
        "message_channel": "test.client",
        "behavior": "instant",
        "payload": {"test_name": "integration test"}
    }

def test_schema_validation_and_config_load(valid_message):
    # Remove a required field to force schema validation failure
    invalid_message = valid_message.copy()
    del invalid_message["event_type"]
    with pytest.raises(ValueError) as exc_info:
        send_to_producer("http://fake-url.com", invalid_message)
    assert "'event_type' is a required property" in str(exc_info.value)

@pytest.mark.skipif(PRODUCER_URL is None, reason="KINDO_MESSAGE_PRODUCER_URL not set")
def test_signed_post_success(valid_message):
    tracking_id = send_to_producer(PRODUCER_URL, valid_message)
    assert isinstance(tracking_id, str) and len(tracking_id) > 0

