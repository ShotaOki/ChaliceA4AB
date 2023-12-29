from typing import List, Type
from chalice_a4ab import (
    Chalice,
    AgentsForAmazonBedrockConfig,
    ParserLambdaAbortException,
    ParserLambdaResponseModel,
)
from chalice_spec.docs import Docs, Operation
from pydantic import BaseModel

# LLMのシチュエーションを定義します
AgentsForAmazonBedrockConfig(
    instructions=(  #
        "あなたはWindowsプログラムを管理しています。"  #
        "受け取った指示から引数を推定して、適切なコマンドを返すことができます。"  #
        "応答はできるだけ丁寧に返答してください。"  #
    )
).apply()

# AppNameはプロジェクト名と合わせてください
app = Chalice(app_name="make_llm")


class HelpInput(BaseModel):
    """
    ヘルプを表示するためのインプットを受け取ります

    ヘルプを表示するためのインプットを受け取ります
    """

    pass


class OpenServerInput(BaseModel):
    """
    ローカル環境にサーバを立てるためのインプットを受け取ります

    ポート番号と、バインドするホストのIPを受け取ります
    """

    port_number: int
    binding_ip: str


class VersionInput(BaseModel):
    """
    アプリケーションのバージョンを返すためのインプットを受け取ります

    アプリケーションのパッケージ名を受け取ります
    """

    package_name: str


class HelpResponse(BaseModel):
    """
    ヘルプを返します

    ヘルプを返します
    """

    info_list: List[str]


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


@app.route("/help", **post_method_define(HelpInput, HelpResponse))
def show_help():
    """
    このアプリが何ができるのか、ヘルプを返します

    このアプリについて質問されたときに、ヘルプ文章を返します
    """
    return HelpResponse(
        info_list=[
            "ヘルプを表示することができます",
            "pythonでサーバを立てることができます。ポート番号を指定できます",
            "pythonにインストールしたパッケージのバージョンを表示することができます",
        ]
    ).model_dump_json()


@app.route("/open_server", **post_method_define(OpenServerInput))
def open_server():
    """
    pythonでサーバを立てます

    ポート番号とバインドするIPアドレスを受け取って、ローカル環境にサーバを立てます。
    ポート番号とIPアドレスは省略することができます。
    """
    # コメントだけを書きます。この関数は呼ばれないため、何もしません
    return None


@app.route("/version", **post_method_define(VersionInput))
def show_version():
    """
    目的のパッケージのバージョンを表示します

    パッケージ名を受け取って、バージョンを表示します
    """
    # コメントだけを書きます。この関数は呼ばれないため、何もしません
    return None


@app.parser_lambda_orchestration()
def orchestration(event: dict, default_result: ParserLambdaResponseModel) -> ParserLambdaResponseModel:
    """
    LLMの解析処理に割り込みます
    """
    if default_result.orchestration_parsed_response:
        input = default_result.orchestration_parsed_response

        # APIの実行前(実行する関数が決定した段階)で、応答に割り込みます
        if input.response_details.action_group_invocation is not None:
            # 実行したAPIのパス名を取得します
            api_name = input.response_details.action_group_invocation.api_name
            api_parameter = input.response_details.action_group_invocation.action_group_input
            # サーバを立てるAPIに割り込みます
            if api_name == "/open_server":
                port_number = api_parameter.get("port_number", {}).get("value", "8080")
                binding_ip = api_parameter.get("binding_ip", {}).get("value", "0.0.0.0")
                # サーバを立てる処理
                raise ParserLambdaAbortException(f"python -m http.server {port_number} -b {binding_ip}")
            # バージョンを調べるAPIに割り込みます
            if api_name == "/version":
                package_name = api_parameter.get("package_name", {}).get("value", None)
                if package_name is None:
                    # パッケージ名が未指定なら、エラーを返す
                    raise ParserLambdaAbortException("パッケージ名が指定されていません。パッケージ名を指定してください")
                # バージョンを調べる処理
                raise ParserLambdaAbortException(f"python -m {package_name} --version")

        # LLMから受け取った応答を整形します
        if input.response_details.agent_final_response is not None:
            # LLMが作成した自然文を取得します
            llm_result = input.response_details.agent_final_response.response_text
            # 今回はechoコマンドに加工します。複数行を出力するために、各行の先頭にechoを入れます
            echo_command = " && ".join([f'echo "{line}"' for line in llm_result.split("\n")])
            # 割り込む対象のAPIではないときに、LLMの応答を加工します
            default_result.orchestration_parsed_response.response_details.agent_final_response.response_text = (
                echo_command
            )

    # 割り込む対象ではないAPIなら、LLMに処理を任せます
    return default_result
