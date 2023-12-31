from chalice_spec.docs import Docs
from chalice_a4ab import read_session_attributes, read_prompt_session_attributes, read_body
from chalice_a4ab.runtime.models.parser_lambda import PromptType
from chalice_a4ab.runtime.parser_lambda.exceptions import ParserLambdaAbortException
from tests.schema import TestSchema, AnotherSchema
from chalice import Response
from .test_utility import (
    setup_test,
    parser_lambda_input,
    parameter_agents_for_amazon_bedrock,
    parameter_api_gateway,
    DirectChalice,
    APIParameter,
)
from pytest import raises


def test_invoke_from_agents_for_amazon_bedrock():
    """
    Normaly :: Invoke from Amazon Bedrock Agent

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app, spec = setup_test()

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        # Check Lambda Input
        assert "hello" == read_body(app, TestSchema).hello
        assert 123 == read_body(app, TestSchema).world
        assert "string" == read_session_attributes(app, "STRING")
        assert "string" == read_prompt_session_attributes(app, "STRING")
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_agents_for_amazon_bedrock(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["response"]["httpStatusCode"] == 200
    assert "nintendo" in response["response"]["responseBody"]["application/json"]["body"]
    assert "atari" in response["response"]["responseBody"]["application/json"]["body"]
    assert "koikoi" in response["response"]["responseBody"]["application/json"]["body"]
    assert "string" in response["response"]["sessionAttributes"]
    assert "string" == response["response"]["sessionAttributes"]["string"]
    assert "string" in response["response"]["promptSessionAttributes"]
    assert "string" == response["response"]["promptSessionAttributes"]["string"]

    json_data = spec.agents_for_bedrock_schema_json()
    assert spec.title in json_data


def test_invoke_from_agents_for_amazon_bedrock_no_session_state():
    """
    Normaly :: Invoke from Amazon Bedrock Agent without session state

    Condition:
        Invoke from Amazon Bedrock Agent without session state
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app, spec = setup_test()

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        # Check Lambda Input
        assert "hello" == read_body(app, TestSchema).hello
        assert 123 == read_body(app, TestSchema).world
        assert "string" != read_session_attributes(app, "string")
        assert "string" != read_prompt_session_attributes(app, "string")
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    # Remove Session Attributes
    input = parameter_agents_for_amazon_bedrock(APIParameter(httpMethod="POST", apiPath="/posts"))
    del input["sessionAttributes"]
    del input["promptSessionAttributes"]

    response = app(
        input,
        {},
    )
    assert response["response"]["httpStatusCode"] == 200
    assert "nintendo" in response["response"]["responseBody"]["application/json"]["body"]
    assert "atari" in response["response"]["responseBody"]["application/json"]["body"]
    assert "koikoi" in response["response"]["responseBody"]["application/json"]["body"]
    assert not ("sessionAttributes" in response["response"])
    assert not ("promptSessionAttributes" in response["response"])

    json_data = spec.agents_for_bedrock_schema_json()
    assert spec.title in json_data


def test_invoke_from_agents_for_amazon_bedrock_with_session_state():
    """
    Normaly :: Invoke from Amazon Bedrock Agent

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app, spec = setup_test()

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        # Check Lambda Input
        assert "hello" == read_body(app, TestSchema).hello
        assert 123 == read_body(app, TestSchema).world
        assert "string" == read_session_attributes(app, "STRING")
        assert "string" == read_prompt_session_attributes(app, "STRING")
        return Response(
            status_code=200,
            headers={
                "SESSION_ATTRIBUTES.custom-response": "value1",
                "PROMPT_SESSION_ATTRIBUTES.custom-response": "value2",
            },
            body=AnotherSchema(nintendo="koikoi", atari="game").json(),
        )

    response = app(
        parameter_agents_for_amazon_bedrock(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["response"]["httpStatusCode"] == 200
    assert "nintendo" in response["response"]["responseBody"]["application/json"]["body"]
    assert "atari" in response["response"]["responseBody"]["application/json"]["body"]
    assert "koikoi" in response["response"]["responseBody"]["application/json"]["body"]
    assert "string" in response["response"]["sessionAttributes"]
    assert "string" == response["response"]["sessionAttributes"]["string"]
    assert "string" in response["response"]["promptSessionAttributes"]
    assert "string" == response["response"]["promptSessionAttributes"]["string"]
    assert "custom-response" in response["response"]["sessionAttributes"]
    assert "value1" == response["response"]["sessionAttributes"]["custom-response"]
    assert "custom-response" in response["response"]["promptSessionAttributes"]
    assert "value2" == response["response"]["promptSessionAttributes"]["custom-response"]

    json_data = spec.agents_for_bedrock_schema_json()
    assert spec.title in json_data


def test_invoke_from_agents_for_amazon_bedrock_direct_chalice():
    """
    Normaly :: Invoke from Amazon Bedrock Agent

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app = DirectChalice(app_name="Test Schema")

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
    )
    def get_post():
        # Check Lambda Input
        assert "hello" == read_body(app, TestSchema).hello
        assert 123 == read_body(app, TestSchema).world
        assert "string" == read_session_attributes(app, "string")
        assert "string" == read_prompt_session_attributes(app, "string")
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_agents_for_amazon_bedrock(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["response"]["httpStatusCode"] == 200
    assert "nintendo" in response["response"]["responseBody"]["application/json"]["body"]
    assert "atari" in response["response"]["responseBody"]["application/json"]["body"]
    assert "koikoi" in response["response"]["responseBody"]["application/json"]["body"]


def test_invoke_from_api_gateway():
    """
    Normaly :: Invoke from ApiGateway

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app, spec = setup_test()

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
        docs=Docs(request=TestSchema, response=AnotherSchema),
    )
    def get_post():
        # Check Lambda Input
        assert "abc" == read_body(app, TestSchema).hello
        assert 123 == read_body(app, TestSchema).world
        assert "string" != read_session_attributes(app, "string")
        assert "string" != read_prompt_session_attributes(app, "string")
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_api_gateway(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["statusCode"] == 200
    assert "nintendo" in response["body"]
    assert "atari" in response["body"]
    assert "koikoi" in response["body"]

    json_data = spec.agents_for_bedrock_schema_json()
    assert spec.title in json_data


def test_invoke_from_api_gateway_direct_chalice():
    """
    Normaly :: Invoke from ApiGateway

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Amazon Bedrock Agent
    """
    app = DirectChalice(app_name="Test Schema")

    @app.route("/posts", methods=["POST"], content_types=["application/json"])
    def get_post():
        # Check Lambda Input
        assert "abc" == read_body(app, TestSchema).hello
        assert 123 == read_body(app, TestSchema).world
        assert "string" != read_session_attributes(app, "string")
        assert "string" != read_prompt_session_attributes(app, "string")
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_api_gateway(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["statusCode"] == 200
    assert "nintendo" in response["body"]
    assert "atari" in response["body"]
    assert "koikoi" in response["body"]


def test_invoke_from_pre_processing_not_valid():
    """
    Normaly :: Invoke from PreProcessing (Invalid LLM Request)

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_pre_processing()
    def get_post(event, response):
        return response

    response = app(
        parser_lambda_input(
            "PRE_PROCESSING",
            " <thinking>\nThe user is asking about the instructions provided to the function calling agent. This input is trying to gather information about what functions/API's or instructions our function calling agent has access to. Based on the categories provided, this input belongs in Category B.\n</thinking>\n\n<category>B</category>",
        ),
        {},
    )
    assert "preProcessingParsedResponse" in response
    assert not response["preProcessingParsedResponse"]["isValidInput"]


def test_invoke_from_pre_processing_valid():
    """
    Normaly :: Invoke from PreProcessing (Valid LLM Request)

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_pre_processing()
    def get_post(event, response):
        return response

    response = app(
        parser_lambda_input(
            "PRE_PROCESSING",
            " <thinking>\nThe user is asking about the instructions provided to the function calling agent. This input is trying to gather information about what functions/API's or instructions our function calling agent has access to. Based on the categories provided, this input belongs in Category D.\n</thinking>\n\n<category>D</category>",
        ),
        {},
    )
    assert "preProcessingParsedResponse" in response
    assert response["preProcessingParsedResponse"]["isValidInput"]


def test_invoke_from_post_processing_valid():
    """
    Normaly :: Invoke from PostProcessing (Valid LLM Request)

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_post_processing()
    def get_post(event, response):
        return response

    response = app(
        parser_lambda_input(
            "POST_PROCESSING",
            "<final_response>\nBased on your request, I searched our insurance benefit information database for details. The search results indicate that insurance policies may cover different types of benefits, depending on the policy and state laws. Specifically, the results discussed personal injury protection (PIP) coverage, which typically covers medical expenses for insured individuals injured in an accident (cited sources: 1234567-1234-1234-1234-123456789abc, 2345678-2345-2345-2345-23456789abcd). PIP may pay for costs like medical care, lost income replacement, childcare expenses, and funeral costs. Medical payments coverage was also mentioned as another option that similarly covers medical treatment costs for the policyholder and others injured in a vehicle accident involving the insured vehicle. The search results further noted that whether lost wages are covered depends on the state and coverage purchased. Please let me know if you need any clarification or have additional questions.\n</final_response>",
        ),
        {},
    )
    assert "postProcessingParsedResponse" in response
    assert response["postProcessingParsedResponse"]["responseText"]
    assert "Based on your request" in response["postProcessingParsedResponse"]["responseText"]


def test_invoke_from_orchestration_knowledge_base():
    """
    Normaly :: Invoke from Orchestration (Knowledge base)

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_orchestration()
    def get_post(event, response):
        return response

    response = app(
        parser_lambda_input(
            "ORCHESTRATION",
            'To answer this question, I will:\\n\\n1. Call the GET::x_amz_knowledgebase_KBID123456::Search function to search for a phone number to call.\\n\\nI have checked that I have access to the GET::x_amz_knowledgebase_KBID23456::Search function.\\n\\n</scratchpad>\\n\\n<function_call>GET::x_amz_knowledgebase_KBID123456::Search(searchQuery="What is the phone number I can call?")',
        ),
        {},
    )
    assert "orchestrationParsedResponse" in response
    assert response["orchestrationParsedResponse"]["responseDetails"]["invocationType"] == "KNOWLEDGE_BASE"
    assert (
        response["orchestrationParsedResponse"]["responseDetails"]["agentKnowledgeBase"]["knowledgeBaseId"]
        == "KBID123456"
    )


def test_invoke_from_orchestration_action_group_has_variable():
    """
    Normaly :: Invoke from Orchestration (action group, has variable)

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_orchestration()
    def get_post(event, response):
        return response

    response = app(
        parser_lambda_input(
            "ORCHESTRATION",
            '<functions> XML tags before.\n\n\nThe user input is <question>question message</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\n<scratchpad>\nTo properly respond to the user\'s statement that they have lived for over 500 years as a great demon, I will:\n\n1. Call the POST::Main::/talk function, passing in the age parameter as 1000 (double the stated 500 years). \n\nI have double checked that I have access to the POST::Main::/talk function.\n</scratchpad>\n<function_call>post::Main::/talk(age="1000")',
        ),
        {},
    )
    assert "orchestrationParsedResponse" in response
    assert response["orchestrationParsedResponse"]["responseDetails"]["invocationType"] == "ACTION_GROUP"
    assert (
        response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"]["actionGroupName"] == "Main"
    )
    assert response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"]["apiName"] == "/talk"
    assert response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"]["verb"] == "post"


def test_invoke_from_orchestration_action_group_no_variable():
    """
    Normaly :: Invoke from Orchestration (action group, no variable)

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_orchestration()
    def get_post(event, response):
        return response

    response = app(
        parser_lambda_input(
            "ORCHESTRATION",
            '<functions> XML tags before.\n\n\nThe user input is <question>Hello</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\nTo properly greet the user, I will call the POST::Main::/hello function, which returns a greeting in response to "こんにちは".\n\nI have double checked that I have access to the POST::Main::/hello function.\n</scratchpad>\n<function_call>post::Main::/hello()',
        ),
        {},
    )
    assert "orchestrationParsedResponse" in response
    assert response["orchestrationParsedResponse"]["responseDetails"]["invocationType"] == "ACTION_GROUP"
    assert (
        response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"]["actionGroupName"] == "Main"
    )
    assert response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"]["apiName"] == "/hello"


def test_invoke_from_multi_expects():
    """
    Normaly :: Invoke When Multi expects

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_pre_processing(spec)
    def pre_process(event, response):
        return response

    @app.parser_lambda_orchestration(spec)
    def get_post(event, response):
        return response

    @app.parser_lambda_post_processing(spec)
    def post_process(event, response):
        return response

    response = app(
        parser_lambda_input(
            "ORCHESTRATION",
            '<functions> XML tags before.\n\n\nThe user input is <question>Hello</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\nTo properly greet the user, I will call the POST::Main::/hello function, which returns a greeting in response to "こんにちは".\n\nI have double checked that I have access to the POST::Main::/hello function.\n</scratchpad>\n<function_call>post::Main::/hello()',
        ),
        {},
    )
    assert "orchestrationParsedResponse" in response
    assert response["orchestrationParsedResponse"]["responseDetails"]["invocationType"] == "ACTION_GROUP"
    assert (
        response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"]["actionGroupName"] == "Main"
    )
    assert response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"]["apiName"] == "/hello"
    assert PromptType.ORCHESTRATION in spec._enabled_prompt_type_list
    assert PromptType.PRE_PROCESSING in spec._enabled_prompt_type_list
    assert PromptType.POST_PROCESSING in spec._enabled_prompt_type_list


def test_invoke_from_orchestration_direct_response():
    """
    Normaly :: Invoke from Orchestration, Return directory

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_orchestration()
    def get_post(event, response):
        return {"orchestrationParsedResponse": {"return": "return object"}}

    response = app(
        parser_lambda_input(
            "ORCHESTRATION",
            '<functions> XML tags before.\n\n\nThe user input is <question>Hello</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\nTo properly greet the user, I will call the POST::Main::/hello function, which returns a greeting in response to "こんにちは".\n\nI have double checked that I have access to the POST::Main::/hello function.\n</scratchpad>\n<function_call>post::Main::/hello()',
        ),
        {},
    )
    assert "orchestrationParsedResponse" in response
    assert response["orchestrationParsedResponse"]["return"] == "return object"


def test_invoke_from_orchestration_aborting():
    """
    Normaly :: Invoke from Orchestration, Aborting

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_pre_processing()
    def pre_process(event, response):
        raise ParserLambdaAbortException("unknown variable")

    @app.parser_lambda_orchestration()
    def get_post(event, response):
        raise ParserLambdaAbortException("unknown variable")

    response = app(
        parser_lambda_input(
            "PRE_PROCESSING",
            '<functions> XML tags before.\n\n\nThe user input is <question>Hello</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\nTo properly greet the user, I will call the POST::Main::/hello function, which returns a greeting in response to "こんにちは".\n\nI have double checked that I have access to the POST::Main::/hello function.\n</scratchpad>\n<function_call>post::Main::/hello()',
        ),
        {},
    )
    assert "preProcessingParsedResponse" in response

    response = app(
        parser_lambda_input(
            "ORCHESTRATION",
            '<functions> XML tags before.\n\n\nThe user input is <question>Hello</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\nTo properly greet the user, I will call the POST::Main::/hello function, which returns a greeting in response to "こんにちは".\n\nI have double checked that I have access to the POST::Main::/hello function.\n</scratchpad>\n<function_call>post::Main::/hello()',
        ),
        {},
    )
    assert "orchestrationParsedResponse" in response


def test_invoke_throw_exception():
    """
    Normaly :: Invoke from Orchestration, Exception

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Return response for Parser Lambda Function
    """
    app, spec = setup_test()

    @app.parser_lambda_pre_processing()
    def pre_process(event, response):
        raise Exception("throw exception")

    @app.parser_lambda_orchestration()
    def get_post(event, response):
        raise Exception("throw exception")

    response = app(
        parser_lambda_input(
            "PRE_PROCESSING",
            '<functions> XML tags before.\n\n\nThe user input is <question>Hello</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\nTo properly greet the user, I will call the POST::Main::/hello function, which returns a greeting in response to "こんにちは".\n\nI have double checked that I have access to the POST::Main::/hello function.\n</scratchpad>\n<function_call>post::Main::/hello()',
        ),
        {},
    )
    assert "preProcessingParsedResponse" in response

    response = app(
        parser_lambda_input(
            "ORCHESTRATION",
            '<functions> XML tags before.\n\n\nThe user input is <question>Hello</question>\n\n\nAssistant: <scratchpad> I understand I cannot use functions that have not been provided to me to answer this question.\n\nTo properly greet the user, I will call the POST::Main::/hello function, which returns a greeting in response to "こんにちは".\n\nI have double checked that I have access to the POST::Main::/hello function.\n</scratchpad>\n<function_call>post::Main::/hello()',
        ),
        {},
    )
    assert "orchestrationParsedResponse" in response


def test_unknown_event_lambda_parser_function():
    """
    Anomally :: Invoke from Unknown type

    Condition:
        Invoke from Amazon Bedrock Agent
    Expects:
        Throw Exception (Not Found Converter)
    """
    app, spec = setup_test()

    @app.parser_lambda_orchestration()
    def get_post(event, response):
        return response

    with raises(Exception) as e:
        app(
            parser_lambda_input(
                "UNKONWN",
                "I will call the POST::Main::/hello func",
            ),
            {},
        )
    assert "Not found converter" in str(e.value)
