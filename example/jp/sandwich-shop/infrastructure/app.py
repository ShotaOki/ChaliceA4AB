#!/usr/bin/env python3

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk
from stacks.chaliceapp import ChaliceApp
from stacks.backend import BackendApp
from pathlib import Path
import json

CDK_AGENT_CONFIG = "cdk-agent-config.json"

with open(str(Path(__file__).parent / CDK_AGENT_CONFIG)) as fp:
    agents_list = json.loads(fp.read())

app = cdk.App()

# スタックを作成する
for agent in agents_list:
    if agent["type"] == "Agent":
        ChaliceApp(app, agent["id"], agent)
    elif agent["type"] == "Backend":
        BackendApp(app, agent["id"])

app.synth()
