from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from chalice_a4ab.runtime.models.bedrock_agent import BedrockAgentModel


class PromptType(Enum):
    ORCHESTRATION = "ORCHESTRATION"
    POST_PROCESSING = "POST_PROCESSING"
    PRE_PROCESSING = "PRE_PROCESSING"
    KNOWLEDGE_BASE_RESPONSE_GENERATION = "KNOWLEDGE_BASE_RESPONSE_GENERATION"


class ParserLambdaInputModel(BaseModel):
    # Parser Lambda Function Input Version
    message_version: str = Field(alias="messageVersion")
    # Invoked Agent Information
    agent: BedrockAgentModel
    # RAW strings from LLM
    invoke_model_raw_response: str = Field(alias="invokeModelRawResponse")
    # Prompt type
    prompt_type: PromptType = Field(alias="promptType")
    # Override type
    override_type: str = Field("OUTPUT_PARSER", alias="overrideType")


class PreProcessingResponseModel(BaseModel):
    is_valid_input: bool = Field(alias="isValidInput")
    rationale: str


class AgentAskUserModel(BaseModel):
    response_text: str = Field(alias="responseText")


class ActionGroupInvocationModel(BaseModel):
    action_group_name: str = Field(alias="actionGroupName")
    api_name: str = Field(alias="apiName")
    verb: str
    action_group_input: Optional[dict] = Field(alias="actionGroupInput")


class AgentKnowledgeBaseModel(BaseModel):
    knowledge_base_id: str = Field(alias="knowledgeBaseId")
    search_query: dict = Field(alias="searchQuery")


class AgentFinalResponseModel(BaseModel):
    response_text: str = Field(alias="responseText")
    citations: dict


class ResponseDetailsModel(BaseModel):
    invocation_type: str = Field(alias="invocationType")
    agent_ask_user: Optional[AgentAskUserModel] = Field(alias="agentAskUser")
    action_group_invocation: Optional[ActionGroupInvocationModel] = Field(
        alias="actionGroupInvocation"
    )
    agent_knowledge_base: Optional[AgentKnowledgeBaseModel] = Field(
        alias="agentKnowledgeBase"
    )
    agent_final_response: Optional[AgentFinalResponseModel] = Field(
        alias="agentFinalResponse"
    )


class ParsingErrorDetailsModel(BaseModel):
    reprompt_response: str = Field(alias="repromptResponse")


class OrchestrationResponseModel(BaseModel):
    rationale: str
    parsing_error_details: Optional[ParsingErrorDetailsModel] = Field(
        alias="parsingErrorDetails"
    )
    response_details: ResponseDetailsModel = Field(alias="responseDetails")


class ParserLambdaResponseModel(BaseModel):
    message_version: Optional[str] = Field(alias="messageVersion")
    prompt_type: PromptType = Field(alias="promptType")
    pre_processing_parsed_response: Optional[PreProcessingResponseModel] = Field(
        alias="preProcessingParsedResponse"
    )
    orchestration_parsed_response: Optional[dict] = Field(
        alias="orchestrationParsedResponse"
    )

    class Config:
        use_enum_values = True
