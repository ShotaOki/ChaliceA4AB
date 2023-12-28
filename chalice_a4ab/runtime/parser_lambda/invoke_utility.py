from chalice_a4ab.runtime.models.parser_lambda import (
    ParserLambdaResponseModel,
    PromptType,
)
from chalice_a4ab.runtime.parser_lambda.agents_parser import (
    AgentsParserFunction,
    is_agents_parser_instance,
)
from chalice_a4ab.runtime.parser_lambda.amazon_example.pre_processing import (
    lambda_handler as pre_processing_lambda_handler,
)
from chalice_a4ab.runtime.parser_lambda.amazon_example.orchestration import (
    lambda_handler as orchestration_lambda_handler,
)
from chalice_a4ab.runtime.parser_lambda.exceptions import create_response_from_expception
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u


def _invoke_agents_with_function(event, context, parser_function, handler) -> dict:
    """
    Invoke agents parser function(Common process)
    """
    parsed = parser_function(event, context)
    parsed_model = u(ParserLambdaResponseModel).parse_obj(parsed)
    handled_parsed_model = handler(event, parsed_model)
    if isinstance(handled_parsed_model, ParserLambdaResponseModel):
        # Return response from pydantic model
        return u(handled_parsed_model).dict(by_alias=True, exclude_none=True)
    # Return response from handler
    return handled_parsed_model


def is_handle_event_agents_parser(target: AgentsParserFunction, event: dict, context: dict) -> bool:
    if is_agents_parser_instance(target) is False:
        # call from mixin class
        return False
    for handler in target._parser_function_handlers:
        if handler.is_handle_event(event, context):
            return True
    return False


def invoke_agents_parser(target: AgentsParserFunction, event: dict, context: dict):
    """
    Invoke agents parser function
    """
    if is_agents_parser_instance(target) is False:
        # call from mixin class
        return False
    failed_event = {}
    try:
        for handler in target._parser_function_handlers:
            if handler.is_handle_event(event, context):
                if handler._prompt_type == PromptType.PRE_PROCESSING:
                    return _invoke_agents_with_function(event, context, pre_processing_lambda_handler, handler)
                if handler._prompt_type == PromptType.ORCHESTRATION:
                    return _invoke_agents_with_function(event, context, orchestration_lambda_handler, handler)
    except Exception as e:
        failed_event = create_response_from_expception(event, e)
    return failed_event
