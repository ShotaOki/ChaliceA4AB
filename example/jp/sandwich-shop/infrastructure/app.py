#!/usr/bin/env python3

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk
from stacks.chaliceapp import ChaliceApp
from pathlib import Path
import json

CDK_AGENT_CONFIG = "cdk-agent-config.json"

with open(str(Path(__file__).parent / CDK_AGENT_CONFIG)) as fp:
    agents_list = json.loads(fp.read())

app = cdk.App()

# 対話エージェントを複数作成する
for agent in agents_list:
    ChaliceApp(app, agent["id"], agent)

app.synth()
