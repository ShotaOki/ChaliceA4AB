from typing import List
from chalice_a4ab.runtime.models.bedrock_agent import (
    BedrockAgentEventModel,
    BedrockAgentPropertyModel,
)
import json
from chalice_a4ab.runtime.model_utility.apigw import empty_api_gateway_event
from chalice_a4ab.runtime.model_utility.bedrock_agent import (
    empty_bedrock_agent_response,
)
from . import EventConverter
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u

# Header key constant : Content-Type
HEADER_KEY_CONTENT_TYPE = "content-type"

# Session attribute key in received event
SESSION_ATTRIBUTE_KEY = "sessionAttributes"
# Prompt session attribute key in received event
PROMPT_SESSION_ATTRIBUTE_KEY = "promptSessionAttributes"
# Session attribute mapping in header
SESSION_ATTRIBUTE_HEADER_PREFIX = "SESSION_ATTRIBUTES"
# Prompt session attribute mapping in header
PROMPT_SESSION_ATTRIBUTE_HEADER_PREFIX = "PROMPT_SESSION_ATTRIBUTES"


class BedrockAgentEventToApiGateway(EventConverter):
    # Content type of the Bedrock Agent event
    _content_type: str

    def __init__(self, content_type: str = "application/json"):
        """
        constructor.

        :param content_type: Content type of the Bedrock Agent event
        """
        super().__init__()
        self._content_type = content_type

    def _parse_value(self, property: BedrockAgentPropertyModel):
        """
        parse Bedrock Agent Property Model to value.

        :param property: Bedrock Agent Property Model
        :return: value
        """
        return property.value

    def _is_contains_properties(self, agent_event: BedrockAgentEventModel):
        """
        check Bedrock Agent Event Model is contains properties.

        :param agent_event: Bedrock Agent Event Model
        :return: bool
        """
        if (
            (agent_event.request_body is not None)
            and (agent_event.request_body.content is not None)
            and (self._content_type in agent_event.request_body.content)
        ):
            return True
        return False

    def convert_request(self, event: dict) -> dict:
        """
        parse event input to other type parameter.

        :param event: Bedrock Agent Event
        :return: Api Gateway Event
        """
        # Event dict convert to pydanerics model
        agent_event: BedrockAgentEventModel = u(BedrockAgentEventModel).parse_obj(event)
        # Setup pydantic empty model for api gateway event
        apigw_event = empty_api_gateway_event()
        apigw_event.requestContext.httpMethod = agent_event.http_method
        apigw_event.requestContext.resourcePath = agent_event.api_path
        apigw_event.headers[HEADER_KEY_CONTENT_TYPE] = self._content_type
        if SESSION_ATTRIBUTE_KEY in event:
            attributes = event[SESSION_ATTRIBUTE_KEY]
            for key in attributes:
                apigw_event.headers[f"{SESSION_ATTRIBUTE_HEADER_PREFIX}.{key}"] = attributes[key]
        if PROMPT_SESSION_ATTRIBUTE_KEY in event:
            attributes = event[PROMPT_SESSION_ATTRIBUTE_KEY]
            for key in attributes:
                apigw_event.headers[f"{PROMPT_SESSION_ATTRIBUTE_HEADER_PREFIX}.{key}"] = attributes[key]
        # Set event body for chalice
        if self._is_contains_properties(agent_event):
            apigw_event.body = json.dumps(
                {
                    prop.name: self._parse_value(prop)
                    for prop in agent_event.request_body.content[self._content_type].properties
                }
            )
        # Return api gateway event
        return u(apigw_event).dict(by_alias=True)

    def convert_response(self, event: dict, response: dict) -> dict:
        """
        parse event response to other type response.

        :param event: Bedrock Agent Event
        :param response: Api Gateway Event that is created by Chalice
        :return: Bedrock Agent Response
        """
        # Event dict convert to pydanerics model
        agent_event: BedrockAgentEventModel = u(BedrockAgentEventModel).parse_obj(event)
        # Setup pydantic empty model for bedrock agent response
        result = empty_bedrock_agent_response()
        result.message_version = "1.0"
        # set from request event
        result.response.action_group = agent_event.action_group
        result.response.api_path = agent_event.api_path
        result.response.http_method = agent_event.http_method
        # set from chalice response
        result.response.http_status_code = response["statusCode"]
        result.response.add_response_body(content_type=self._content_type, body=response["body"])
        # Set Session Attributes from input events
        for key, value in agent_event.session_attributes.items():
            result.response.add_session_attributes(key, value)
        for key, value in agent_event.prompt_session_attributes.items():
            result.response.add_prompt_session_attributes(key, value)
        # Set Session Attributes from Header response
        if "headers" in response:
            for key, value in response["headers"].items():
                uppercase_key: str = key.upper()
                split_key: List[str] = key.split(".", maxsplit=2)
                if len(split_key) >= 2:
                    # Read Header "SESSION_ATTRIBUTES.attribute_name": "value"
                    if uppercase_key.startswith(f"{SESSION_ATTRIBUTE_HEADER_PREFIX}."):
                        result.response.add_session_attributes(split_key[1], value)
                    # Read Header "PROMPT_SESSION_ATTRIBUTES.attribute_name": "value"
                    if uppercase_key.startswith(f"{PROMPT_SESSION_ATTRIBUTE_HEADER_PREFIX}."):
                        result.response.add_prompt_session_attributes(split_key[1], value)
        return u(result).dict(by_alias=True, exclude_none=True)
