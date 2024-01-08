from typing import List, Optional
import boto3
from uuid import uuid4
from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from chalice_a4ab.cli.arg_input import ProfileInput
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u
import argparse
import json

input_parser = argparse.ArgumentParser(description="Chalice A4AB CLI")
input_parser.add_argument("command", type=str, help="command")
input_parser.add_argument("input_text", type=str, help="input text")
input_parser.add_argument("--session-id", type=str, help="session id")
input_parser.add_argument("--agent-id", type=str, help="agent id")
input_parser.add_argument("--agent-alias-id", type=str, help="agent alias id")
input_parser.add_argument("--end-session", action="store_true", help="end session")
input_parser.add_argument("--enable-trace", action="store_true", help="enable trace")
input_parser.add_argument("--region", type=str, help="region name")
input_parser.add_argument("--profile", type=str, help="profile name")


class SessionState(BaseModel):
    session_attributes: dict = Field(alias="sessionAttributes")
    prompt_session_attributes: dict = Field(alias="promptSessionAttributes")


class RunAgentParameter(BaseModel):
    agent_id: str = Field(alias="agentId")
    agent_alias_id: str = Field(alias="agentAliasId")
    session_id: Optional[str] = Field(str(uuid4()), alias="sessionId")
    input_text: Optional[str] = Field(alias="inputText")
    end_session: bool = Field(False, alias="endSession")
    enable_trace: bool = Field(False, alias="enableTrace")
    session_state: Optional[SessionState] = Field(None, alias="sessionState")

    _boto3_parameter: dict = PrivateAttr({})

    def to_boto3_parameter(self) -> dict:
        return self._boto3_parameter


def read_run_agent_parameter(input_args: List[str]) -> RunAgentParameter:
    """
    Read agents conig from command options
    """
    try:
        if input_args[0] != "invoke":
            return None
        arg = input_parser.parse_args(input_args)
        # Read Profile
        profile = arg.profile
        region = arg.region
        # if profile and region is empty, set default region
        if (profile is None) and (region is None):
            region = "us-east-1"
        # Set Profile
        input = ProfileInput(region_name=region, profile_name=profile)
        parameter = {
            "agentId": arg.agent_id,
            "agentAliasId": arg.agent_alias_id,
            "sessionId": arg.session_id,
            "inputText": arg.input_text,
            "endSession": arg.end_session,
            "enableTrace": arg.enable_trace,
        }
        for key in list(parameter.keys()):
            if parameter[key] is None:
                del parameter[key]
        # Parse By Pydantic
        result: RunAgentParameter = u(RunAgentParameter).parse_obj(parameter)
        result._boto3_parameter = u(input).dict(exclude_none=True, by_alias=True)
        return result
    except ValidationError as e:
        # Pydantic Validation Error
        print(e)
        if arg.command == "invoke":
            # e.g. no input text, no agent id
            exit(0)
        return None
    except Exception:
        return None


def invoke(session_parameter: dict, agent_parameter: RunAgentParameter):
    """
    Invoke Agents for Amazon Bedrock Runtime

    :return LLM Message
    """
    client = boto3.Session(**session_parameter).client("bedrock-agent-runtime")
    # Down flag :: End Session
    request_parameter = u(agent_parameter).dict(exclude_none=True, by_alias=True)
    request_parameter["endSession"] = False
    # Invoke Agent
    response = client.invoke_agent(**request_parameter)
    result_lines: List[str] = []
    event_stream = response["completion"]
    for event in event_stream:
        # If we received chunk event, print line
        if "chunk" in event:
            data = event["chunk"]["bytes"].decode("utf-8")
            result_lines.append(data)
        if agent_parameter.enable_trace and "trace" in event:
            data = event["trace"]
            print(json.dumps(data, indent=2))
    # If Enabled End Session flg, End Session
    if agent_parameter.end_session:
        request_parameter["endSession"] = True
        client.invoke_agent(**request_parameter)

    return "".join(result_lines)
