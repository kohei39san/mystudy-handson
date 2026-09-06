import json
import os

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


def invoke(prompt: str) -> requests.Response:
    url = os.environ["API_INVOKE_URL"]
    region = os.environ.get("AWS_REGION", boto3.session.Session().region_name or "us-east-1")
    body = json.dumps({"prompt": prompt}).encode("utf-8")
    credentials = boto3.Session().get_credentials()
    if credentials is None:
        raise RuntimeError("AWS credentials are required")

    request = AWSRequest(
        method="POST",
        url=url,
        data=body,
        headers={"content-type": "application/json"},
    )
    SigV4Auth(credentials.get_frozen_credentials(), "execute-api", region).add_auth(request)
    prepared = request.prepare()
    return requests.request(
        method=prepared.method,
        url=prepared.url,
        headers=dict(prepared.headers),
        data=prepared.body,
        timeout=60,
    )


if __name__ == "__main__":
    response = invoke(os.environ.get("PROMPT", "Hello from the IAM authenticated client"))
    response.raise_for_status()
    print(response.text)