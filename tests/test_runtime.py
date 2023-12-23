import json
from chalice_spec.docs import Docs
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
from tests.schema import TestSchema, AnotherSchema
from chalice_a4ab import (
    Chalice,
    AgentsForAmazonBedrockConfig,
    agents_for_amazon_bedrock,
)
from pydantic import BaseModel
from chalice.app import Chalice as _Chalice


def setup_test():
    spec = AgentsForAmazonBedrockConfig(
        title="Test Schema",
        instructions="Test Agents for Amazon Bedrock, You can use this API with Amazon Bedrock Agent.",
    )
    app = Chalice(app_name="test", spec=spec)
    return app, spec


class APIParameter(BaseModel):
    apiPath: str
    httpMethod: str


class EmptySchema(BaseModel):
    pass


@agents_for_amazon_bedrock()
class DirectChalice(_Chalice):
    pass


def parameter_agents_for_amazon_bedrock(parameter: APIParameter):
    return {
        "messageVersion": "1.0",
        "agent": {
            "name": "string",
            "id": "string",
            "alias": "string",
            "version": "string",
        },
        "inputText": "string",
        "sessionId": "string",
        "actionGroup": "string",
        "apiPath": parameter.apiPath,
        "httpMethod": parameter.httpMethod,
        "parameters": [{"name": "string", "type": "string", "value": "string"}],
        "requestBody": {
            "content": {
                "application/json": {
                    "properties": [
                        {"name": "hello", "type": "string", "value": "hello"},
                        {"name": "world", "type": "int", "value": "123"},
                    ]
                }
            }
        },
        "sessionAttributes": {
            "string": "string",
        },
        "promptSessionAttributes": {"string": "string"},
    }


def parameter_api_gateway(parameter: APIParameter):
    return {
        "resource": parameter.apiPath,
        "path": parameter.apiPath,
        "httpMethod": parameter.httpMethod,
        "requestContext": {
            "resourcePath": parameter.apiPath,
            "httpMethod": parameter.httpMethod,
            "path": parameter.apiPath,
            "accountId": "",
            "apiId": "",
            "authorizer": {},
            "identity": {"sourceIp": "0.0.0.0"},
            "protocol": "",
            "requestId": "",
            "requestTime": "",
            "requestTimeEpoch": 0,
            "stage": "",
        },
        "headers": {"content-type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": {},
        "multiValueQueryStringParameters": {},
        "pathParameters": {},
        "stageVariables": "",
        "body": json.dumps({"hello": "abc", "world": 123}),
        "isBase64Encoded": False,
    }


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
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_agents_for_amazon_bedrock(
            APIParameter(httpMethod="POST", apiPath="/posts")
        ),
        {},
    )
    assert response["response"]["httpStatusCode"] == 200
    assert (
        "nintendo" in response["response"]["responseBody"]["application/json"]["body"]
    )
    assert "atari" in response["response"]["responseBody"]["application/json"]["body"]
    assert "koikoi" in response["response"]["responseBody"]["application/json"]["body"]

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
    app = DirectChalice(app_name="main-app")

    @app.route(
        "/posts",
        methods=["POST"],
        content_types=["application/json"],
    )
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_agents_for_amazon_bedrock(
            APIParameter(httpMethod="POST", apiPath="/posts")
        ),
        {},
    )
    assert response["response"]["httpStatusCode"] == 200
    assert (
        "nintendo" in response["response"]["responseBody"]["application/json"]["body"]
    )
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
    app = DirectChalice(app_name="main-app")

    @app.route("/posts", methods=["POST"], content_types=["application/json"])
    def get_post():
        return AnotherSchema(nintendo="koikoi", atari="game").json()

    response = app(
        parameter_api_gateway(APIParameter(httpMethod="POST", apiPath="/posts")),
        {},
    )
    assert response["statusCode"] == 200
    assert "nintendo" in response["body"]
    assert "atari" in response["body"]
    assert "koikoi" in response["body"]


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
