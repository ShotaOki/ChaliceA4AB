from chalice_a4ab.runtime.models.apigw import APIGatewayProxyEventModel
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u


def is_api_gateway_event(event: dict) -> bool:
    """
    Check event is api gateway event.
    """
    try:
        u(APIGatewayProxyEventModel).parse_obj(event)
        return True
    except Exception:
        # throw pydantic -> event is not API Gateway Event
        return False


def empty_api_gateway_event() -> APIGatewayProxyEventModel:
    """
    Create empty api gateway event.
    """
    return u(APIGatewayProxyEventModel).parse_obj(
        {
            "resource": "",
            "path": "",
            "httpMethod": "GET",
            "headers": {},
            "multiValueHeaders": {},
            "queryStringParameters": {},
            "multiValueQueryStringParameters": {},
            "requestContext": {
                "accountId": "",
                "apiId": "",
                "authorizer": {},
                "httpMethod": "GET",
                "identity": {"sourceIp": "0.0.0.0"},
                "path": "",
                "protocol": "",
                "requestId": "",
                "requestTime": "",
                "requestTimeEpoch": 0,
                "resourcePath": "",
                "stage": "",
            },
            "body": "{}",
            "isBase64Encoded": False,
        }
    )
