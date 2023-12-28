from chalice_a4ab.agents_for_amazon_bedrock_config import AgentsForAmazonBedrockConfig
from chalice_a4ab.runtime.api_runtime import (
    mixin_api_runtime,
)
from chalice.app import Chalice as AWSChalice
from chalice_a4ab.runtime.parser_lambda.agents_parser import mixin_agents_parser


def agents_for_amazon_bedrock(spec_initializer=None):
    """
    Chalice class override to support Agents for Amazon Bedrock

    :param spec_initializer: initializer function for APISpec
    """

    def _agents_for_amazon_bedrock(cls):
        def wrapper(*args, **kwargs) -> AWSChalice:
            # global _spec
            # Read Spec from kwargs
            config = AgentsForAmazonBedrockConfig.get_global_config()
            if "spec" in kwargs:
                if isinstance(kwargs["spec"], AgentsForAmazonBedrockConfig):
                    # Set AgentsForAmazonBedrockConfig as spec key word argument
                    spec = spec_initializer(kwargs["spec"])
                    kwargs["spec"] = spec
                    AgentsForAmazonBedrockConfig.apply_spec(spec)
                else:
                    # Update Spec from kwargs
                    AgentsForAmazonBedrockConfig.apply_spec(kwargs["spec"])
            elif (spec_initializer is not None) and (config is not None):
                # Update Spec from initializer
                spec = spec_initializer(config)
                # Set Spec to kwargs
                kwargs["spec"] = spec
                AgentsForAmazonBedrockConfig.apply_spec(spec)
            if "app_name" in kwargs:
                if config is not None:
                    config.title = kwargs["app_name"]
                spec = AgentsForAmazonBedrockConfig.get_global_spec()
                if spec is not None:
                    spec.title = kwargs["app_name"]

            # Rewrite Mixin Functions
            mixin_api_runtime(cls)
            mixin_agents_parser(cls)
            return cls(*args, **kwargs)

        return wrapper

    return _agents_for_amazon_bedrock
