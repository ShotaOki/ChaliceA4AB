#!/usr/bin/env python3

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk
from stacks.chaliceapp import ChaliceApp


AGENTS = [
    {
        # 顧客に対して注文をたずねる
        "id": "ask-to-order",
        "path": "ask-to-order",
    }
]

app = cdk.App()

# 対話エージェントを複数作成する
for agent in AGENTS:
    ChaliceApp(app, agent["id"], agent)

app.synth()
