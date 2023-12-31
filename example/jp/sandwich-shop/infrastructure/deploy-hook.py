from pathlib import Path

from chalice_a4ab import cli as template_root
from chalice_a4ab.cli.cdk import read_agent_config_from_file_path, execute_process_from_cdk_hook, read_config_profile
from chalice_a4ab.cli.management import init, sync, delete
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))


args = read_config_profile(sys.argv[1:])
cfn_template = str(Path(template_root.__file__).parent / "template.yaml")
project_root = Path(__file__).parent.parent

CDK_AGENT_CONFIG = "cdk-agent-config.json"


def process(method_on_exist_stack=None, method_on_no_exist_stack=None):
    """
    Execute process
    """
    with open(str(Path(__file__).parent / CDK_AGENT_CONFIG)) as fp:
        agents_list = json.loads(fp.read())

    for agent in agents_list:
        # Get Application Agents Information
        agent_config = read_agent_config_from_file_path(project_root, agent["path"])
        # Update Method
        execute_process_from_cdk_hook(
            agent_config=agent_config,
            session_parameter=args.s3_config(),
            agent_id=agent["id"],
            cfn_template=cfn_template,
            method_on_exist_stack=method_on_exist_stack,
            method_on_no_exist_stack=method_on_no_exist_stack,
        )


if args.command == "deploy":
    process(method_on_exist_stack=sync, method_on_no_exist_stack=init)
elif args.command == "delete":
    process(method_on_exist_stack=delete)
