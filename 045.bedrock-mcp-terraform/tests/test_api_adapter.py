import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock, patch


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "api_adapter.py"


def load_module():
    spec = importlib.util.spec_from_file_location("api_adapter", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch("boto3.client", return_value=Mock()):
        spec.loader.exec_module(module)
    return module


def test_handler_invokes_agentcore_runtime():
    module = load_module()
    module.agentcore_client.invoke_agent_runtime.return_value = {
        "response": [b"Hello", b" from AgentCore"]
    }
    module.os.environ["AGENTCORE_RUNTIME_ARN"] = "arn:aws:bedrock-agentcore:example"

    result = module.handler({"body": json.dumps({"prompt": "Hello"})}, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"response": "Hello from AgentCore"}
    call = module.agentcore_client.invoke_agent_runtime.call_args.kwargs
    assert call["agentRuntimeArn"] == "arn:aws:bedrock-agentcore:example"
    assert call["qualifier"] == "DEFAULT"
    assert json.loads(call["payload"]) == {"prompt": "Hello"}


def test_handler_rejects_missing_prompt():
    module = load_module()

    result = module.handler({"body": "{}"}, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"]) == {"message": "prompt is required"}
    module.agentcore_client.invoke_agent_runtime.assert_not_called()


def test_handler_rejects_invalid_json():
    module = load_module()

    result = module.handler({"body": "not-json"}, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"]) == {"message": "request body must be valid JSON"}
    module.agentcore_client.invoke_agent_runtime.assert_not_called()


def test_handler_rejects_base64_requests():
    module = load_module()

    try:
        module.handler({"body": "{}", "isBase64Encoded": True}, None)
    except ValueError as error:
        assert str(error) == "Base64 encoded requests are not supported"
    else:
        raise AssertionError("Expected ValueError")


def test_handler_returns_json_runtime_response():
    module = load_module()
    module.agentcore_client.invoke_agent_runtime.return_value = {
        "response": {"message": "Hello"}
    }
    module.os.environ["AGENTCORE_RUNTIME_ARN"] = "arn:aws:bedrock-agentcore:example"

    result = module.handler({"body": json.dumps({"prompt": "Hello"})}, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"response": {"message": "Hello"}}


def test_handler_returns_single_byte_response():
    module = load_module()
    module.agentcore_client.invoke_agent_runtime.return_value = {
        "response": b'{"message":"Hello"}'
    }
    module.os.environ["AGENTCORE_RUNTIME_ARN"] = "arn:aws:bedrock-agentcore:example"

    result = module.handler({"body": json.dumps({"prompt": "Hello"})}, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"response": '{"message":"Hello"}'}
