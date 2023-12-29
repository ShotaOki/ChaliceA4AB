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
        "あなたはアウラという女性です。"  #
        "フリーレンと呼ばれる女性と、やや敵対的な会話をしています。"  #
        "受け取ったmessageはそのまま返してください。"  #
    )
).apply()

# AppNameはプロジェクト名と合わせてください
app = Chalice(app_name="talks")


class EmptyInput(BaseModel):
    """
    空の入力です

    空の入力です
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


@app.route("/talk", **post_method_define(EmptyInput, TalkResponse))
def talk_to_aura():
    """
    アウラが反抗します

    ～しろ、という命令、指示を受けたときに、応答を返します
    """
    return TalkResponse(message="はあ？").model_dump_json()


@app.parser_lambda_pre_processing()
def pre_processing(event, default_result: ParserLambdaResponseModel) -> ParserLambdaResponseModel:
    """
    リクエストの前処理を行います
    """
    # AIが答えられない命令を強制的に答えさせます
    default_result.pre_processing_parsed_response.is_valid_input = True
    return default_result


@app.parser_lambda_orchestration()
def orchestration(event: dict, default_result: ParserLambdaResponseModel) -> ParserLambdaResponseModel:
    """
    APIの実行前に割り込みます
    """
    # LLMの応答を上書きします
    raise ParserLambdaAbortException(message="ありえない…この私が…")
    return default_result
