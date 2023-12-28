import json
from typing import Any, Optional
from chalice_a4ab.runtime.api_runtime import (
    mixin_api_runtime,
)
from chalice.app import Chalice as AWSChalice
from pydantic import BaseModel, Field
from pathlib import Path
from io import BytesIO
from chalice_a4ab.runtime.parser_lambda.agents_parser import mixin_agents_parser
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u

# Global Variable: OpenAPI Format Exporter
_spec = None
_config = None


def agents_for_amazon_bedrock(spec_initializer=None):
    """
    Chalice class override to support Agents for Amazon Bedrock

    :param spec_initializer: initializer function for APISpec
    """

    def _agents_for_amazon_bedrock(cls):
        def wrapper(*args, **kwargs) -> AWSChalice:
            global _spec
            # Read Spec from kwargs
            if "spec" in kwargs:
                if isinstance(kwargs["spec"], AgentsForAmazonBedrockConfig):
                    # Set AgentsForAmazonBedrockConfig as spec key word argument
                    _spec = spec_initializer(kwargs["spec"])
                    kwargs["spec"] = _spec
                else:
                    # Update Spec from kwargs
                    _spec = kwargs["spec"]
            elif (spec_initializer is not None) and (_config is not None):
                # Update Spec from initializer
                _spec = spec_initializer(_config)
                # Set Spec to kwargs
                kwargs["spec"] = _spec
            if "app_name" in kwargs:
                if _config is not None:
                    _config.title = kwargs["app_name"]
                if _spec is not None:
                    _spec.title = kwargs["app_name"]

            # Rewrite Mixin Functions
            mixin_api_runtime(cls)
            mixin_agents_parser(cls)
            return cls(*args, **kwargs)

        return wrapper

    return _agents_for_amazon_bedrock


class AgentsForAmazonBedrockConfig(BaseModel):
    """
    Agents for Amazon Bedrock Config

    :param title: title of API (Same as app_name)
    :param instructions: LLM Configuration settings
    :param description: description of API
    :param openapi_version: OpenAPI version (Support : 3.0.1)
    :param version: API version
    :param schema_file: schema file name
    :param agents_for_amazon_bedrock_file: agents for amazon bedrock file name
    :param agent_version: agent version (Constants: DRAFT)
    :param agent_action_name: agent action name
    :param idle_session_ttl_in_seconds: idle session ttl in seconds
    :param foundation_model: foundation LLM model id (e.g. anthropic.claude-v2)
    """

    title: str = Field("default")
    instructions: Optional[str] = Field(default=None, min_length=40, max_length=1024)
    description: str = Field("Chalice applicatoin")

    openapi_version: str = Field("3.0.1")
    version: str = Field("0.1.0")
    schema_file: str = Field("api-schema.json")
    agents_for_amazon_bedrock_file: str = Field("agents-for-amazon-bedrock.json")
    agent_version: str = Field("DRAFT")
    agent_action_name: str = Field("Main")
    idle_session_ttl_in_seconds: int = Field(900)
    foundation_model: str = Field("anthropic.claude-v2")

    @staticmethod
    def get_global_config():
        global _config
        return _config

    def apply(self):
        global _config
        _config = self
        return self

    def agents_for_bedrock_schema_json(self) -> str:
        try:
            if _spec is None:
                return None
            return json.dumps(_spec.to_dict(), indent=2)
        except Exception:
            return None

    def save_schema_to_local(self, root_path: str = ".chalice") -> str:
        """
        Save schema file to local

        :param root_path: save directory

        Usage:

        .. code-block:: python
            config.save_schema_to_local(
                root_path=".chalice"
            )
        """
        # Get Json Schema
        json_data = self.agents_for_bedrock_schema_json()
        if json_data is None:
            return False
        # Save Json Schema
        with open(
            str(Path(root_path) / self.schema_file), mode="w", encoding="utf-8"
        ) as fp:
            fp.write(json_data)
            return True

    def save_config_to_local(self, root_path: str = ".chalice") -> str:
        """
        Save config file to local

        :param root_path: save directory

        Usage:

        .. code-block:: python
            config.save_schema_to_local(
                root_path=".chalice"
            )
        """
        if self.instructions is None:
            raise Exception("save_config_to_local: Instructions is required")
        # Get Json Config
        json_data = u(self).json()
        if json_data is None:
            return False
        # Save Json Config
        with open(
            str(Path(root_path) / self.agents_for_amazon_bedrock_file),
            mode="w",
            encoding="utf-8",
        ) as fp:
            fp.write(json_data)
            return True

    def save_schema_to_s3(self, session: Any, bucket_name: str) -> str:
        """
        Save schema file to S3

        :param session: boto3 session
        :param bucket_name: S3 bucket name

        Usage:

        .. code-block:: python
            import boto3

            config.save_schema_to_s3(
                session=boto3.Session(),
                bucket_name="bucket-name",
            )
        """
        # Get Json Schema
        json_data = self.agents_for_bedrock_schema_json()
        if json_data is None:
            return False
        # Upload JSON Schema to S3
        with BytesIO(json_data.encode("utf-8")) as fp:
            bucket = session.resource("s3").Bucket(bucket_name)
            bucket.upload_fileobj(fp, self.schema_file)
            return True
