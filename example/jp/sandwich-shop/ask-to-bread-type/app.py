import json
from typing import Type
from uuid import uuid4
from chalice_a4ab import (
    Chalice,
    AgentsForAmazonBedrockConfig,
    ParserLambdaAbortException,
    ParserLambdaResponseModel,
)
from chalice_spec.docs import Docs, Operation
from pydantic import BaseModel

AgentsForAmazonBedrockConfig(
    instructions=(  #
        "あなたはサンドウィッチショップのスタッフをしています。"  #
        "パンの種類を聞き取って、それを反映することができます。"  #
        "注文の要求には丁寧に答えるようにしてください。"  #
    )
).apply()

# AppNameはプロジェクト名と合わせてください
app = Chalice(app_name="agent-what-bread-type")


class OrderInput(BaseModel):
    """
    注文の入力です

    空の入力を受け取ります
    """

    pass


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


@app.route("/help", **post_method_define(OrderInput, TalkResponse))
def help():
    """
    パンについての質問に答えます

    パンについての質問に答えます
    """
    return (
        "選ぶことのできるパンは、ホワイト、ウィート、ハニーオーツ、セサミです。"
        "ホワイトはほんのり甘みのある、プレーンなパンです。"
        "ウィートは小麦胚芽入りで、ハチミツの甘味を加えたパンです。"
        "セサミは香ばしいごまをトッピングしたパンです。"
        "ハニーオーツはハチミツ、オーツ、大豆のオーツミックスをトッピングしたパンです。"
    )


@app.route("/white", **post_method_define(OrderInput, TalkResponse))
def accept_white():
    """
    ホワイトのパンを受け取ります

    「ホワイト」のパンの注文を受け取ります。ほんのり甘みのある、プレーンなパンです。普通のパンです。
    カロリーは179キロカロリーです。
    """
    return None


@app.route("/wheat", **post_method_define(OrderInput, TalkResponse))
def accept_wheat():
    """
    ホワイトのパンを受け取ります

    「ウィート」のパンの注文を受け取ります。小麦胚芽入りで、ハチミツの甘味を加えたパンです。健康的なパンです。
    カロリーは180キロカロリーです。
    """
    return None


@app.route("/seasame", **post_method_define(OrderInput, TalkResponse))
def accept_seasame():
    """
    セサミのパンを受け取ります

    「セサミ」のパンの注文を受け取ります。香ばしいごまをトッピングしたパンです。
    カロリーは196キロカロリーです。
    """
    return None


@app.route("/honey_oats", **post_method_define(OrderInput, TalkResponse))
def accept_honey_oats():
    """
    ハニーオーツのパンを受け取ります

    「ハニーオーツ」のパンの注文を受け取ります。ハチミツ、オーツ、大豆のオーツミックスをトッピングしたパンです。
    カロリーは190キロカロリーです。
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
            # APIに割り込みます
            if api_name != "/help":
                # LLMの応答を上書きします
                raise ParserLambdaAbortException(
                    message=json.dumps(
                        {
                            "action": "json_control.update_order",
                            "value": {"bread": api_name.replace("/", "")},
                        }
                    )
                )

    return default_result
