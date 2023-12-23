from chalice_a4ab.runtime.models.bedrock_agent import (
    BedrockAgentEventModel,
    BedrockAgentResponseModel,
)
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u


def is_bedrock_agent_event(event: dict) -> bool:
    """
    Check event is bedrock agent event.
    """
    try:
        u(BedrockAgentEventModel).parse_obj(event)
        return True
    except Exception:
        # throw pydantic -> event is not Bedrock Agent Event
        return False


def empty_bedrock_agent_event() -> BedrockAgentEventModel:
    """
    Create empty bedrock agent event.
    """
    return u(BedrockAgentEventModel).parse_obj(
        {
            "messageVersion": "1.0",
            "agent": {
                "name": "",
                "id": "",
                "alias": "",
                "version": "",
            },
            "inputText": "",
            "sessionId": "",
            "actionGroup": "",
            "apiPath": "",
            "httpMethod": "",
            "parameters": [],
            "requestBody": {"content": {}},
        }
    )


def empty_bedrock_agent_response() -> BedrockAgentResponseModel:
    """
    Create empty bedrock agent response.
    """
    return u(BedrockAgentResponseModel).parse_obj(
        {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "",
                "apiPath": "",
                "httpMethod": "",
                "httpStatusCode": 0,
                "responseBody": {},
            },
        }
    )
