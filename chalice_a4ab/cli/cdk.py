from pathlib import Path
import argparse
from typing import List
from chalice_a4ab import AgentsForAmazonBedrockConfig
from chalice_a4ab.cli.arg_input import ProfileInput
from chalice_a4ab.cli.management import read_identity, CallerIdentity
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u
from importlib.util import spec_from_file_location, module_from_spec
from pydantic import BaseModel

input_parser = argparse.ArgumentParser(description="Chalice A4AB from CDK")
input_parser.add_argument("command", type=str, help="command")
input_parser.add_argument("--region", type=str, help="region name")
input_parser.add_argument("--profile", type=str, help="profile name")


class CdkProfileConfig(BaseModel):
    command: str
    profile: ProfileInput

    def s3_config(self):
        return u(self.profile).dict(exclude_none=True, by_alias=True)


def read_config_profile(args: List[str]):
    """
    Read cdk config from args
    """
    input = input_parser.parse_args(args)
    profile = input.profile
    region = input.region
    # if profile and region is empty, set default region
    if (profile is None) and (region is None):
        region = "us-east-1"
    return CdkProfileConfig(command=input.command, profile=ProfileInput(profile_name=profile, region_name=region))


def read_agent_config_from_file_path(root_path: Path, agent_path: str):
    """
    Read agent config from app.py

    :root_path: project root path
    :agent_path: app.py parent path
    """
    # Get Application Agents Information
    spec = spec_from_file_location("app", root_path / agent_path / "app.py")
    lib = module_from_spec(spec)
    spec.loader.exec_module(lib)
    return lib.AgentsForAmazonBedrockConfig.get_global_config()


def read_api_handler_arn_from_output(
    identity: CallerIdentity, agent_id: str, lambda_arn_output_key: str = "APIHandlerArn"
):
    """
    Read Lambda ARN from output
    """
    cfn = identity.session.resource("cloudformation")
    stack = cfn.Stack(agent_id)
    return [output["OutputValue"] for output in stack.outputs if output["OutputKey"] == lambda_arn_output_key][0]


def read_from_output(identity: CallerIdentity, stack_id: str):
    """
    Read output from stack
    """
    cfn = identity.session.resource("cloudformation")
    stack = cfn.Stack(stack_id)
    return {output["OutputKey"]: output["OutputValue"] for output in stack.outputs}


def is_exist_stack(identity: CallerIdentity, stack_name: str):
    """
    Check is exist stack
    """
    cfn = identity.session.client("cloudformation")
    try:
        cfn.describe_stacks(StackName=stack_name)
    except Exception:
        return False
    return True


def execute_process_from_cdk_hook(
    agent_config: AgentsForAmazonBedrockConfig,
    session_parameter: dict,
    agent_id: str,
    cfn_template: str,
    method_on_exist_stack,
    method_on_no_exist_stack,
) -> CallerIdentity:
    """
    Execute process from cdk
    """
    # Get Caller Identity
    identity: CallerIdentity = read_identity(agent_config, session_parameter)
    # Update DefaultLambdaARN
    identity.DefaultLambdaArn = read_api_handler_arn_from_output(identity, agent_id)
    # Deploy Resource
    if not is_exist_stack(identity, identity.stack_name):
        if method_on_no_exist_stack is not None:
            # Init project
            method_on_no_exist_stack(identity, agent_config, cfn_template)
    else:
        if method_on_exist_stack is not None:
            # Sync project
            method_on_exist_stack(identity, agent_config, cfn_template)
    # Return Caller Identity
    return identity
