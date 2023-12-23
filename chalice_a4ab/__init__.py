from typing import Type
from chalice.app import Chalice as AWSChalice

from .chalice_plugin import (  # noqa: F401
    agents_for_amazon_bedrock,
    AgentsForAmazonBedrockConfig,
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


# Public functions
Chalice: Type[AWSChalice] = _Chalice
