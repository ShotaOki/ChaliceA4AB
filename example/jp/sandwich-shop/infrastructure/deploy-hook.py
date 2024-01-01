from pathlib import Path

from chalice_a4ab import cli as template_root
from chalice_a4ab.cli.cdk import (
    read_agent_config_from_file_path,
    execute_process_from_cdk_hook,
    read_config_profile,
    read_from_output,
)
from chalice_a4ab import AgentsForAmazonBedrockConfig
from chalice_a4ab.cli.management import CallerIdentity, init, read_identity, sync, delete, info
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))


args = read_config_profile(sys.argv[1:])
cfn_template = str(Path(template_root.__file__).parent / "template.yaml")
project_root = Path(__file__).parent.parent

CDK_AGENT_CONFIG = "cdk-agent-config.json"


def read_nested_config(value: dict, key: str):
    key_list = key.split(".")
    result = value
    for k in key_list:
        if k in result:
            result = result[k]
    return result


def process(method_on_exist_stack=None, method_on_no_exist_stack=None, update_export_config: bool = False):
    """
    Execute process
    """
    with open(str(Path(__file__).parent / CDK_AGENT_CONFIG)) as fp:
        stack_list = json.loads(fp.read())

    # Get Caller Identity
    default_identity: CallerIdentity = read_identity(AgentsForAmazonBedrockConfig(), args.s3_config())
    export_config = {}

    for stack in stack_list:
        stack_id: str = stack["id"]
        stack_type: str = stack["type"]
        if stack_type == "Agent":
            # Get Application Agents Information
            agent_config = read_agent_config_from_file_path(project_root, stack["path"])
            # Update Method
            agent_identity = execute_process_from_cdk_hook(
                agent_config=agent_config,
                session_parameter=args.s3_config(),
                agent_id=stack_id,
                cfn_template=cfn_template,
                method_on_exist_stack=method_on_exist_stack,
                method_on_no_exist_stack=method_on_no_exist_stack,
            )
            if update_export_config:
                output = info(agent_identity, True)
                for export_stack_key, output_key in stack["export"].items():
                    export_key: str = f"VITE_{stack_id}_{export_stack_key}"
                    export_key = export_key.upper().replace("-", "_")
                    export_config[export_key] = read_nested_config(output, output_key)
        else:
            if update_export_config:
                output = read_from_output(default_identity, stack_id)
                for export_stack_key, output_key in stack["export"].items():
                    export_key: str = f"VITE_{stack_id}_{export_stack_key}"
                    export_key = export_key.upper().replace("-", "_")
                    export_config[export_key] = read_nested_config(output, output_key)

    if update_export_config:
        print(export_config)


if args.command == "deploy":
    process(method_on_exist_stack=sync, method_on_no_exist_stack=init, update_export_config=True)
elif args.command == "delete":
    process(method_on_exist_stack=delete)
