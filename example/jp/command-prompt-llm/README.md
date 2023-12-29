# サンプル

## このサンプルの目的

- Agents for AB とローカルアプリの連携例を提示します

## 前提条件

- bedrock の名前で AWS アカウントのプロファイルがあること
- プロファイルのデフォルトリージョンが us-east-1 であること

## デプロイの方法

1. ライブラリをインストールして、事前準備をします

   ```bash
   pip install -U chalice chalice-spec==0.7.0 chalice-a4ab boto3 pydantic
   ```

2. Chalice のデプロイコマンドを実行します

   ```bash
   chalice deploy --profile bedrock
   ```

3. ChaliceA4AB のデプロイコマンドを実行します

   ```bash
   chalice init --profile bedrock --region us-east-1
   ```

## アプリの実行

make_llm.bat を編集して、AGENT_ID、AGENT_ALIAS_ID、PROFILE を設定します

AGENT_ID は以下のコマンドで調べることができます

1. 事前準備

   ```bash
   chalice-a4ab info --profile bedrock --region us-east-1
   ```

2. コマンドの実行

   ```bash
   make_llm.bat アプリは何ができますか？
   ```

   ```bash
   make_llm.bat ポート番号8080でサーバを立ててください
   ```

   ```bash
   make_llm.bat pipのバージョンを教えてください
   ```

## 修正後の更新

1. Chalice を更新します

   ```bash
   chalice deploy --profile bedrock
   ```

2. ChaliceA4AB の更新コマンドを実行します

   ```bash
   chalice sync --profile bedrock --region us-east-1
   ```

## プロジェクトの削除

1. Chalice を更新します

   ```bash
   chalice delete --profile bedrock
   ```

2. ChaliceA4AB の更新コマンドを実行します

   ```bash
   chalice delete --profile bedrock --region us-east-1
   ```
