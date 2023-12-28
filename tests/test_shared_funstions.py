from chalice_a4ab.runtime.api_runtime import APIRuntimeHandler, is_api_runtime_instance
from chalice_a4ab.runtime.converter import EventConverter
from chalice_a4ab.runtime.model_utility.apigw import (
    empty_api_gateway_event,
    is_api_gateway_event,
)
from chalice_a4ab.runtime.model_utility.bedrock_agent import (
    empty_bedrock_agent_event,
    empty_bedrock_agent_response,
    is_bedrock_agent_event,
)
from chalice_a4ab.runtime.parser_lambda.agents_parser import is_agents_parser_instance
from chalice_a4ab.runtime.parser_lambda.invoke_utility import invoke_agents_parser, is_handle_event_agents_parser
from .test_utility import setup_test


def test_converter_base_class():
    """
    Normaliy :: Call base class method

    Expects:
        Base class is not changed received parameter
    """
    assert EventConverter().convert_request({"Hello": "world"})["Hello"] == "world"
    assert EventConverter().convert_response({}, {"Hello": "world"})["Hello"] == "world"


def test_utility_functions_create_empty_base_models():
    """
    Normally :: Create empty base models

    Expects:
        No Assertion Errors
    """
    assert is_api_gateway_event(empty_api_gateway_event().dict(by_alias=True))
    assert is_bedrock_agent_event(empty_bedrock_agent_event().dict(by_alias=True))
    assert not is_api_gateway_event(empty_bedrock_agent_event().dict(by_alias=True))
    assert not is_bedrock_agent_event(empty_api_gateway_event().dict(by_alias=True))
    empty_bedrock_agent_response()


def test_is_handler_instance():
    """
    Normally :: Check handler instance

    Expects:
        No Assertion Errors
    """
    app, spec = setup_test()
    assert is_api_runtime_instance(app)
    assert is_agents_parser_instance(app)
    assert not is_api_runtime_instance(object())
    assert not is_agents_parser_instance(object())

    class TestTargetClass:
        pass

    setattr(TestTargetClass, "_parser_function_handlers", [])
    assert not is_agents_parser_instance(TestTargetClass())
    setattr(TestTargetClass, "parser_lambda_pre_processing", [])
    assert not is_agents_parser_instance(TestTargetClass())

    assert not is_handle_event_agents_parser({}, {}, {})
    assert not invoke_agents_parser({}, {}, {})


def test_no_runtime_request():
    """
    Anomally :: called no implements class

    Expects:

    """

    app, spec = setup_test()
    app._runtime = None

    result = app({}, {})
    print(result)
