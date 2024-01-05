# サンドウィッチショップ

複数のエージェントを CDK で管理して、注文のフェーズごとに異なるエージェントを利用するサンプルです。

## QuickStart

1.  **CDK と依存ライブラリのインストール**  
    この README のあるディレクトリで以下のコマンドを実行します

    ```bash
    npm install -g aws-cdk
    ```

    ```bash
    pip install -r requirements.txt
    ```

1.  **CDK を初期化します**  
    あらかじめ、AWS のアカウントを設定しておきます。  
    リージョンは**us-east-1 を設定**します。

    infrastructure のディレクトリで、Bootstrap を実行します

    ```bash
    cdk bootstrap
    ```

1.  **デプロイ**  
    Bootstrap を実行したあと、以下のコマンドでデプロイをします

    ```bash
    cdk deploy --all && python3 deploy-hook.py deploy

    # もしAWSのプロファイルがdefaultでないなら、上のコマンドの代わりに、以下のコマンドを実行します
    cdk deploy --all --profile ${プロファイル名} && python3 deploy-hook.py deploy --profile ${プロファイル名} --region us-east-1
    ```

    デプロイコマンドを実行すると、frontend のディレクトリに、.env のファイルが作成されます

1.  **Web アプリのビルド**  
    frontend のディレクトリで以下のコマンドを実行します。

    ```bash
    npm install
    ```

    ```bash
    npm run dev
    ```

1.  **ブラウザを開く**  
    以下の URL をブラウザで開きます。

    http://localhost:5173

    ブラウザで開いた後、「アカウントを作成する」タブを選んで、ログインユーザーを作成します。

## 更新と削除

1.  **更新**  
    ソースコードを更新する場合も、デプロイと同じコマンドを実行します

    ```bash
    cdk deploy --all && python3 deploy-hook.py deploy

    # もしプロファイルがdefaultでないなら、上のコマンドの代わりに、以下のコマンドを実行します
    cdk deploy --all --profile ${プロファイル名} && python3 deploy-hook.py deploy --profile ${プロファイル名} --region us-east-1
    ```

1.  **削除**  
    プロジェクトを削除するときは、以下のコマンドを実行します

    ```bash
    python3 deploy-hook.py delete && cdk destroy --all

    # もしプロファイルがdefaultでないなら、上のコマンドの代わりに、以下のコマンドを実行します
    python3 deploy-hook.py delete --profile ${プロファイル名} --region us-east-1 && cdk destroy --all --profile ${プロファイル名}
    ```
