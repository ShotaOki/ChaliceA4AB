from typing import Type
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
        "注文の詳細情報を確認して、それを追記することができます。"  #
        "注文の要求には丁寧に答えるようにしてください。"  #
    )
).apply()

# AppNameはプロジェクト名と合わせてください
app = Chalice(app_name="agent-what-sandwich-option")


class OrderInput(BaseModel):
    """
    注文の入力です

    注文の情報を格納します。数をcountsとして受け取ります。
    「はい」や肯定やYESは1、「いいえ」や否定やNOは0として数えます。
    """

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


@app.route("/accept_property", **post_method_define(OrderInput, TalkResponse))
def talk_to_aura():
    """
    数量を受け取ります（注文はオーケストレーションで割り込みます）

    注文の数量を受け取ります。数量をcountsとして受け取ります。
    「はい」や肯定やYESは1、「いいえ」や否定やNOは0として数えます。
    """
    return None


@app.parser_lambda_orchestration()
def orchestration(event: dict, default_result: ParserLambdaResponseModel) -> ParserLambdaResponseModel:
    """
    APIの実行前に割り込みます
    """
    # LLMの応答を上書きします
    # raise ParserLambdaAbortException(message="ありえない…この私が…")
    return default_result
