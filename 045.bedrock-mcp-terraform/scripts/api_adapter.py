import json
import os
import uuid

import boto3


agentcore_client = boto3.client("bedrock-agentcore")


def handler(event, _context):
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raise ValueError("Base64 encoded requests are not supported")

    try:
        request = json.loads(body)
    except json.JSONDecodeError:
        return response(400, {"message": "request body must be valid JSON"})

    prompt = request.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return response(400, {"message": "prompt is required"})

    runtime_response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=os.environ["AGENTCORE_RUNTIME_ARN"],
        runtimeSessionId=str(uuid.uuid4()),
        payload=json.dumps({"prompt": prompt}).encode("utf-8"),
        qualifier="DEFAULT",
    )

    return response(200, {"response": read_runtime_response(runtime_response)})


def read_runtime_response(runtime_response):
    runtime_body = runtime_response.get("response", "")
    if isinstance(runtime_body, (bytes, bytearray)):
        return runtime_body.decode("utf-8")
    if isinstance(runtime_body, str):
        return runtime_body
    if isinstance(runtime_body, dict):
        return runtime_body
    return "".join(
        chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
        for chunk in runtime_body
    )


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }