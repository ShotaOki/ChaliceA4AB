import json
from pydantic import BaseModel
from chalice import Chalice as _Chalice
from chalice_a4ab import Chalice
from chalice_a4ab import AgentsForAmazonBedrockConfig, agents_for_amazon_bedrock


class APIParameter(BaseModel):
    apiPath: str
    httpMethod: str


class EmptySchema(BaseModel):
    pass


@agents_for_amazon_bedrock()
class DirectChalice(_Chalice):
    pass


def setup_test():
    spec = AgentsForAmazonBedrockConfig(
        title="Test Schema",
        instructions="Test Agents for Amazon Bedrock, You can use this API with Amazon Bedrock Agent.",
    )
    app = Chalice(app_name="Test Schema", spec=spec)
    return app, spec


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


def parser_lambda_input(prompt_type: str, raw_response: str):
    return {
        "messageVersion": "1.0",
        "agent": {
            "name": "string",
            "id": "string",
            "alias": "string",
            "version": "string",
        },
        "invokeModelRawResponse": raw_response,
        "promptType": prompt_type,
        "overrideType": "OUTPUT_PARSER",
    }
