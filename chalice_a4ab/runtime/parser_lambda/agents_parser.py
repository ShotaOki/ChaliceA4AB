from typing import Any, Callable, List
from chalice_a4ab.runtime.models.parser_lambda import (
    ParserLambdaInputModel,
    PromptType,
)
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u


class ParserFunctionEventHandler:
    _handler: Callable[..., Any]
    _prompt_type: PromptType

    def __init__(self, prompt_type: PromptType, handler: Callable[..., Any]):
        self._prompt_type = prompt_type
        self._handler = handler

    def __call__(self, event: dict, context: dict):
        return self._handler(event, context)

    def _check_event_type(
        self, required_type: PromptType, event: dict, context: dict
    ) -> bool:
        try:
            response: ParserLambdaInputModel = u(ParserLambdaInputModel).parse_obj(
                event
            )
            if response.prompt_type == required_type:
                return True
            return False
        except Exception:
            return False

    def is_handle_event(self, event: dict, context: dict) -> bool:
        return self._check_event_type(self._prompt_type, event, context)


class AgentsParserFunction:
    _parser_function_handlers: List[ParserFunctionEventHandler] = []

    def parser_lambda_pre_processing(self):
        def register_handler(event_function: Callable[..., Any]):
            wrapper = ParserFunctionEventHandler(
                PromptType.PRE_PROCESSING, event_function
            )
            self._parser_function_handlers.append(wrapper)

        return register_handler

    def parser_lambda_orchestration(self):
        def register_handler(event_function: Callable[..., Any]):
            wrapper = ParserFunctionEventHandler(
                PromptType.ORCHESTRATION, event_function
            )
            self._parser_function_handlers.append(wrapper)

        return register_handler


def is_agents_parser_instance(target: AgentsParserFunction) -> bool:
    """
    Check Instance: Mixin AgentsParserFunction
    """
    if hasattr(target, "_parser_function_handlers") is False:
        return False
    if hasattr(target, "parser_lambda_pre_processing") is False:
        return False
    if hasattr(target, "parser_lambda_orchestration") is False:
        return False
    return True


def mixin_agents_parser(cls):
    """
    Create mixin: AgentsParserFunction
    """
    # Rewrite Mixin Functions
    setattr(cls, "_parser_function_handlers", [])
    setattr(
        cls,
        "parser_lambda_pre_processing",
        AgentsParserFunction.parser_lambda_pre_processing,
    )
    setattr(
        cls,
        "parser_lambda_orchestration",
        AgentsParserFunction.parser_lambda_orchestration,
    )
