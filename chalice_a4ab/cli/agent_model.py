from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from chalice_a4ab.runtime.models.parser_lambda import PromptType


class InferenceConfigurationModel(BaseModel):
    temperature: float
    top_p: float = Field(..., alias="topP")
    top_k: int = Field(..., alias="topK")
    maximum_length: int = Field(..., alias="maximumLength")
    stop_sequences: List[str] = Field(..., alias="stopSequences")


class PromptConfigurationsModel(BaseModel):
    prompt_type: str = Field(..., alias="promptType")
    prompt_creation_mode: str = Field(..., alias="promptCreationMode")
    prompt_state: Optional[str] = Field(..., alias="promptState")
    base_prompt_template: Optional[str] = Field(..., alias="basePromptTemplate")
    inference_configuration: Optional[InferenceConfigurationModel] = Field(..., alias="inferenceConfiguration")
    parser_mode: str = Field(..., alias="parserMode")


class PromptOverrideConfigurationModel(BaseModel):
    prompt_configurations: List[PromptConfigurationsModel] = Field(..., alias="promptConfigurations")
    override_lambda: Optional[str] = Field(None, alias="overrideLambda")


class AgentModelEditable(BaseModel):
    agent_id: str = Field(..., alias="agentId")
    agent_name: str = Field(..., alias="agentName")
    instruction: Optional[str] = Field(None, alias="instruction")
    foundation_model: Optional[str] = Field(None, alias="foundationModel")
    description: Optional[str] = Field(None, alias="description")
    idle_session_ttl_in_seconds: Optional[int] = Field(None, alias="idleSessionTTLInSeconds")
    agent_resource_role_arn: Optional[str] = Field(None, alias="agentResourceRoleArn")
    customer_encryption_key_arn: Optional[str] = Field(None, alias="customerEncryptionKeyArn")
    prompt_override_configuration: Optional[PromptOverrideConfigurationModel] = Field(
        None, alias="promptOverrideConfiguration"
    )

    def set_enable_configration(self, prompt_type: PromptType, enable: bool):
        for configration in self.prompt_override_configuration.prompt_configurations:
            if configration.prompt_type == prompt_type.value:
                if enable:
                    configration.prompt_creation_mode = "OVERRIDDEN"
                    configration.parser_mode = "OVERRIDDEN"
                else:
                    configration.prompt_creation_mode = "DEFAULT"
                    configration.parser_mode = "DEFAULT"
                    configration.prompt_state = None
                    configration.inference_configuration = None
                    configration.base_prompt_template = None


class AgentModelReadonly(BaseModel):
    agent_arn: str = Field(..., alias="agentArn")
    agent_version: Optional[str] = Field(None, alias="agentVersion")
    client_token: Optional[str] = Field(None, alias="clientToken")
    agent_status: Optional[str] = Field(None, alias="agentStatus")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    prepared_at: Optional[datetime] = Field(None, alias="preparedAt")
    failure_reasons: Optional[List[str]] = Field(None, alias="failureReasons")
    recommended_actions: Optional[List[str]] = Field(None, alias="recommendedActions")
