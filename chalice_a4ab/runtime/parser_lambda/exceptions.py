from chalice_a4ab.runtime.models.parser_lambda import (
    ParserLambdaResponseModel,
    ParserLambdaInputModel,
    PromptType,
    PreProcessingResponseModel,
    OrchestrationResponseModel,
    ResponseDetailsModel,
)
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u


class ParserLambdaAbortException(Exception):
    def __init__(self, message: str):
        self.message = message


def create_response_from_expception(input_event: dict, exception: Exception) -> dict:
    input: ParserLambdaInputModel = u(ParserLambdaInputModel).parse_obj(input_event)
    message = "Failed in parse lambda"

    if isinstance(exception, ParserLambdaAbortException):
        message = exception.message

    response = ParserLambdaResponseModel(messageVersion=input.message_version, promptType=input.prompt_type)
    if input.prompt_type == PromptType.PRE_PROCESSING:
        response.pre_processing_parsed_response = PreProcessingResponseModel(isValidInput=False, rationale=message)
    elif input.prompt_type == PromptType.ORCHESTRATION:
        response.orchestration_parsed_response = OrchestrationResponseModel(
            rationale=message,
            responseDetails=u(ResponseDetailsModel).parse_obj(
                {
                    "invocationType": "FINISH",
                    "agentFinalResponse": {"responseText": message},
                }
            ),
        )
    return u(response).dict(by_alias=True, exclude_none=True)
