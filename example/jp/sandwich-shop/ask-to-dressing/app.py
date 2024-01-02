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
        "パンのドレッシングを聞き取って、それを反映することができます。"  #
        "注文の要求には丁寧に答えるようにしてください。"  #
    )
).apply()

# AppNameはプロジェクト名と合わせてください
app = Chalice(app_name="agent-what-dressing")


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

    パンについての質問に答えます。
    教えてください、どうですか、といった言葉が入っているときは、このメソッドで質問に答えてください。
    """
    return (
        "選ぶことのできるパンは、ホワイト、ウィート、ハニーオーツ、セサミです。"
        "ホワイトはほんのり甘みのある、プレーンなパンです。"
        "ウィートは小麦胚芽入りで、ハチミツの甘味を加えたパンです。"
        "セサミは香ばしいごまをトッピングしたパンです。"
        "ハニーオーツはハチミツ、オーツ、大豆のオーツミックスをトッピングしたパンです。"
    )


@app.route("/bazil", **post_method_define(OrderInput, TalkResponse))
def accept_bazil():
    """
    バジルソースを受け取ります

    「バジルソース」のドレッシングの注文を受け取ります。
    """
    return None


@app.route("/mayonnaise", **post_method_define(OrderInput, TalkResponse))
def accept_mayonnaise():
    """
    マヨネーズを受け取ります

    「マヨネーズ」のドレッシングの注文を受け取ります。小麦胚芽入りで、ハチミツの甘味を加えたパンです。健康的なパンです。
    カロリーは180キロカロリーです。
    """
    return None


@app.route("/wasabi", **post_method_define(OrderInput, TalkResponse))
def accept_wasabi():
    """
    わさび醤油を受け取ります

    「わさび醤油」のドレッシングの注文を受け取ります。しょうゆとわさびを使った、和風の、辛いドレッシングです。
    """
    return None


@app.route("/oil", **post_method_define(OrderInput, TalkResponse))
def accept_oil():
    """
    オイル、ビネガー、塩コショウのドレッシングを受け取ります

    「オイル＆ビネガー、塩コショウ」のドレッシングの注文を受け取ります。塩コショウとオリーブオイル、ビネガーを使ったドレッシングです。
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
                bread_map = {
                    "/bazil": "バジルソース",
                    "/mayonnaise": "マヨネーズ",
                    "/wasabi": "わさび醤油ソース",
                    "/oil": "オイル＆ビネガー 塩コショウ",
                }
                # LLMの応答を上書きします
                raise ParserLambdaAbortException(
                    message=json.dumps(
                        {
                            "action": "json_control.update_order",
                            "value": {"dressing": bread_map.get(api_name, "-")},
                        }
                    )
                )

    return default_result
