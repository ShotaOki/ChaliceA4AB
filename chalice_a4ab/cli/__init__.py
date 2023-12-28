import sys
import os

from chalice_a4ab import AgentsForAmazonBedrockConfig

from .management import init, sync, delete, show, read_identity
from pathlib import Path
from importlib import import_module
import argparse

sys.path.append(str(Path(os.getcwd())))

input_parser = argparse.ArgumentParser(description="Chalice A4AB CLI")
input_parser.add_argument("command", type=str, help="command", default="help")
input_parser.add_argument("--bucket", type=str, help="bucket name", default="")
input_parser.add_argument("--region", type=str, help="region name", default="us-east-1")
input_parser.add_argument("--profile", type=str, help="profile name", default="default")
input_parser.add_argument(
    "--appname",
    type=str,
    help="chalice main file name (default = app.py)",
    default="app",
)


def main():
    """
    Main Function
    """
    try:
        # Parse Input Parameter
        args = input_parser.parse_args(sys.argv[1:])
        # Parse from chalice/app.py
        app_module = import_module("app", package=args.appname)
        # Get Config from chalice/app.py
        config: AgentsForAmazonBedrockConfig = app_module.AgentsForAmazonBedrockConfig.get_global_config()
        # Get Template File
        template_file = str(Path(__file__).parent / "template.yaml")
        # Get Identity (Boto3 Config)
        identity = read_identity(config, args.region, args.profile, args.bucket)
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
        else:
            print("Usage: ")
            print("    chalice-a4ab ${command}")
            print("Commands:")
            print("    init: Initialize AWS Resources")
            print("    sync: Sync AWS Resources with current app.py source")
            print("    delete: Delete AWS Resources")
            print("    show: Show OpenAPI document")
    except Exception as e:
        print("Failed to execute")
        print(e)
        return
