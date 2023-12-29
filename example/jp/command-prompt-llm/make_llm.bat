@echo OFF

REM chalice-a4ab infoで取得したAGENT_IDとAGENT_ALIAS_IDを設定します
SET AGENT_ID=XXXXXXXXXXXXX
SET AGENT_ALIAS_ID=XXXXXXXXXXXXX
SET PROFILE=default
SET REGION=us-east-1

REM Agents for Amazon Bedrockからコマンドを取得します
setlocal
for /f "usebackq delims=" %%A in (`chalice-a4ab invoke %1 --agent-id %AGENT_ID% --agent-alias-id %AGENT_ALIAS_ID% --end-session --profile %PROFILE% --region %REGION%`) do set COMMAND=%%A

REM コマンドの内容を表示します
REM echo %COMMAND%

REM もし問題ないのならエンターキーを押下します
REM pause

REM コマンドを実行します
%COMMAND%
