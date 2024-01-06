from typing import Type
from chalice.app import Chalice as AWSChalice
from chalice_a4ab.utility.parser import (  # noqa: F401
    read_session_attributes,
    read_prompt_session_attributes,
    read_body,
)
from chalice_a4ab.runtime.parser_lambda.agents_parser import AgentsParserFunction
from chalice_a4ab.runtime.parser_lambda.exceptions import ParserLambdaAbortException  # noqa: F401
from .chalice_plugin import (  # noqa: F401
    agents_for_amazon_bedrock,
)
from .agents_for_amazon_bedrock_config import AgentsForAmazonBedrockConfig  # noqa: F401
from chalice_a4ab.runtime.models.parser_lambda import (  # noqa: F401
    ParserLambdaInputModel,
    ParserLambdaResponseModel,
    PreProcessingResponseModel,
    OrchestrationResponseModel,
    PromptType,
)
from chalice_a4ab.model_types import (  # noqa: F401
    ModelTypesAntropicClaudeV1Instant,
    ModelTypesAntropicClaudeV2,
    ModelTypesAntropicClaudeV2_1,
)

try:
    from chalice_spec import ChaliceWithSpec, PydanticPlugin
    from apispec import APISpec

    def spec_initializer(config: AgentsForAmazonBedrockConfig) -> APISpec:
        return APISpec(
            title=config.title,
            openapi_version=config.openapi_version,
            version=config.version,
            plugins=[PydanticPlugin()],
        )

    @agents_for_amazon_bedrock(spec_initializer=spec_initializer)
    class _Chalice(ChaliceWithSpec):
        pass

except Exception:

    @agents_for_amazon_bedrock()
    class _Chalice(AWSChalice):
        pass


# Define Class Type
class ChaliceType(AWSChalice, AgentsParserFunction):
    pass


# Public functions
Chalice: Type[ChaliceType] = _Chalice
