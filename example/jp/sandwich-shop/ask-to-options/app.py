import json
from typing import Type
from chalice_a4ab import (
    Chalice,
    read_session_attributes,
    AgentsForAmazonBedrockConfig,
    ParserLambdaAbortException,
    ParserLambdaResponseModel,
)
from chalice_spec.docs import Docs, Operation
from pydantic import BaseModel

AgentsForAmazonBedrockConfig(
    instructions=(  #
        "あなたはサンドウィッチショップのスタッフをしています。"  #
        "注文の結果を確認して、オーダーを発行することができます。"  #
        "注文の要求には丁寧に答えるようにしてください。"  #
    )
).apply()

# AppNameはプロジェクト名と合わせてください
app = Chalice(app_name="agent-what-sandwich-option")


class OrderInput(BaseModel):
    """
    注文を確定する

    注文を確定する
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


@app.route("/confirm", **post_method_define(OrderInput, TalkResponse))
def confirm():
    """
    注文を確定します

    注文を確定します。
    """
    current_state = read_session_attributes(app, "STATE", {})
    print(current_state)

    return TalkResponse(message="注文を承りました").model_dump_json()


@app.route("/cancel", **post_method_define(OrderInput, TalkResponse))
def cancel():
    """
    注文をキャンセルします

    注文をキャンセルします。
    """
    return TalkResponse(message="注文をキャンセルしました").model_dump_json()


@app.parser_lambda_orchestration()
def orchestration(event: dict, default_result: ParserLambdaResponseModel) -> ParserLambdaResponseModel:
    """
    LLMの解析処理に割り込みます
    """
    if default_result.orchestration_parsed_response:
        input = default_result.orchestration_parsed_response

        # LLMから受け取った応答を整形します
        if input.response_details.agent_final_response is not None:
            # 割り込む対象のAPIではないときに、LLMの応答を加工します
            default_result.orchestration_parsed_response.response_details.agent_final_response.response_text = (
                json.dumps(
                    {
                        "action": "json_control.update_partial",
                        "value": {"commitOrder": True},
                    }
                )
            )

    # 割り込む対象ではないAPIなら、LLMに処理を任せます
    return default_result
