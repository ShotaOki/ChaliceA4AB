from typing import Type
from chalice_a4ab import (
    Chalice,
    AgentsForAmazonBedrockConfig,
    ParserLambdaAbortException,
    ParserLambdaResponseModel,
)
from chalice_spec.docs import Docs, Operation
from pydantic import BaseModel
import json
from uuid import uuid4

AgentsForAmazonBedrockConfig(
    instructions=(  #
        "あなたはサンドウィッチショップのスタッフをしています。"  #
        "注文を受け取り、それを記録することができます。"  #
        "注文の要求には丁寧に答えるようにしてください。"  #
    )
).apply()

# AppNameはプロジェクト名と合わせてください
app = Chalice(app_name="agent-what-sandwich-is-need")


class OrderInput(BaseModel):
    """
    注文の入力です

    注文の情報を格納します。商品名をname、数をcountsとして受け取ります。
    数は省略することができます。
    """

    # 商品名です
    name: str
    # 数量です
    counts: int


class TalkResponse(BaseModel):
    """
    応答を返します

    応答を返します
    """

    message: str


def post_method_define(input_cls: Type[BaseModel], output_cls: Type[BaseModel] = TalkResponse):
    """
    POSTメソッドの共通部品を設定する便利関数です
    """
    return {
        "methods": ["POST"],
        "docs": Docs(
            post=Operation(
                request=input_cls,
                response=output_cls,
            )
        ),
    }


@app.route("/accept_order", **post_method_define(OrderInput, TalkResponse))
def talk_to_aura():
    """
    注文を受け取ります（注文はオーケストレーションで割り込みます）

    サンドイッチの注文を受け取ります。商品名をname、数量をcountsとして受け取ります。
    数量は省略することができます。
    """
    return None


@app.parser_lambda_orchestration()
def orchestration(event: dict, default_result: ParserLambdaResponseModel) -> ParserLambdaResponseModel:
    """
    APIの実行前に割り込みます
    """
    if default_result.orchestration_parsed_response:
        input = default_result.orchestration_parsed_response

        # APIの実行前(実行する関数が決定した段階)で、応答に割り込みます
        if input.response_details.action_group_invocation is not None:
            # 実行したAPIのパス名を取得します
            api_name = input.response_details.action_group_invocation.api_name
            api_parameter = input.response_details.action_group_invocation.action_group_input
            # サーバを立てるAPIに割り込みます
            if api_name == "/accept_order":
                name = api_parameter.get("name", {}).get("value", "-")
                counts = api_parameter.get("counts", {}).get("value", "1")
                # LLMの応答を上書きします
                raise ParserLambdaAbortException(
                    message=json.dumps(
                        {
                            "action": "json_control.append_order",
                            "value": {"id": str(uuid4()), "name": name, "count": int(counts)},
                        }
                    )
                )

    return default_result
