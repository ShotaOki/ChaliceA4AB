import sys
import os

from chalice_a4ab import AgentsForAmazonBedrockConfig

from .management import init, sync, delete, show, read_identity, info
from .arg_input import read_args
from .run_agent import read_run_agent_parameter, invoke
from pathlib import Path
from importlib import import_module

sys.path.append(str(Path(os.getcwd())))


def main():
    """
    Main Function
    """
    try:
        # Parse Run Agent Parameter
        invoke_args = read_run_agent_parameter(sys.argv[1:])
        if invoke_args is not None:
            print(invoke(invoke_args.to_boto3_parameter(), invoke_args))
            return
        # Parse Input Parameter
        args = read_args(sys.argv[1:])
        # Parse from chalice/app.py
        app_module = import_module("app", package=args.appname)
        # Get Config from chalice/app.py
        config: AgentsForAmazonBedrockConfig = app_module.AgentsForAmazonBedrockConfig.get_global_config()
        # Get Template File
        template_file = str(Path(__file__).parent / "template.yaml")
        # Get Identity (Boto3 Config)
        identity = read_identity(config, args.to_boto3_parameter(), default_bucket_name=args.bucket)
        # Required Parameter Check
        if (config.instructions is None) or len(config.instructions) == 0:
            print("Please set instructions in config")
            return
        if (config.description is None) or len(config.description) == 0:
            print("Please set description in config")
            return
        if (config.title is None) or len(config.title) == 0:
            print("Please set title in config")
            return
        # Execute Command
        if args.command == "init":
            init(identity, config, template_file)
        elif args.command == "sync":
            sync(identity, config, template_file)
        elif args.command == "delete":
            delete(identity, config, template_file)
        elif args.command == "show":
            show(config)
        elif args.command == "info":
            info(identity)
        else:
            print("Usage: ")
            print("    chalice-a4ab ${command}")
            print("Commands:")
            print("    init: Initialize AWS Resources")
            print("    sync: Sync AWS Resources with current app.py source")
            print("    delete: Delete AWS Resources")
            print("    show: Show OpenAPI document")
            print("    info: Show information about AWS resources")
    except Exception as e:
        print("Failed to execute")
        print(e)
        return
