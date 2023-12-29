# サンプル

## このサンプルの目的

- ParserLambda のそれぞれの割り込み関数の実装例を提示します

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
