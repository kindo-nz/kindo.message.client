import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import Session

def signed_post(url: str, payload: dict, region: str, service: str) -> requests.Response:
    session = Session()
    credentials = session.get_credentials()
    request = AWSRequest(
        method="POST",
        url=url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    SigV4Auth(credentials, service, region).add_auth(request)
    return requests.post(url, data=request.body, headers=dict(request.headers))