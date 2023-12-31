# サンドウィッチショップ

複数のエージェントをCDKで管理して、注文のフェーズごとに異なるエージェントを利用するサンプルです。

## QuickStart

  $ npm install -g aws-cdk

  $ pip install -r requirements.txt

infrastructureのディレクトリで、Bootstrapを実行します

  $ cdk bootstrap

Bootstrapを実行したあと、デプロイをします

  $ cdk deploy --all && python3 deploy-hook.py deploy

プロジェクトを削除するときは、以下のコマンドを実行します

  $ python3 deploy-hook.py delete && cdk delete --all

