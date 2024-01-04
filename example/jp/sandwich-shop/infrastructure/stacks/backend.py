try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk

import json
from aws_cdk.aws_cognito_identitypool_alpha import (
    IdentityPool,
    UserPoolAuthenticationProvider,
    IdentityPoolAuthenticationProviders,
)

Duration = cdk.Duration
UserPool = cdk.aws_cognito.UserPool
PasswordPolicy = cdk.aws_cognito.PasswordPolicy
SignInAliases = cdk.aws_cognito.SignInAliases
AuthFlow = cdk.aws_cognito.AuthFlow
Role = cdk.aws_iam.Role
PolicyDocument = cdk.aws_iam.PolicyDocument
PolicyStatement = cdk.aws_iam.PolicyStatement
Policy = cdk.aws_iam.Policy
Effect = cdk.aws_iam.Effect
FederatedPrincipal = cdk.aws_iam.FederatedPrincipal
Output = cdk.CfnOutput
Stack = cdk.Stack


class BackendApp(cdk.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # スタック情報を参照する
        stack = Stack.of(self)

        # 認証情報のユーザープールを定義する
        self.user_pool = UserPool(
            self,
            "UserPool",
            password_policy=PasswordPolicy(
                require_uppercase=True, require_symbols=True, require_digits=True, min_length=8
            ),
            self_sign_up_enabled=True,
            sign_in_aliases=SignInAliases(username=False, email=True),
        )
        self.client = self.user_pool.add_client(
            "ApplicationClient",
            id_token_validity=Duration.days(1),
            auth_flows=AuthFlow(user_password=True, user_srp=True),
        )
        # 権限を管理できるよう設定する
        self.identity_pool = IdentityPool(
            self,
            "IdentityPool",
            allow_unauthenticated_identities=False,
            authentication_providers=IdentityPoolAuthenticationProviders(
                user_pools=[UserPoolAuthenticationProvider(user_pool=self.user_pool, user_pool_client=self.client)]
            ),
        )
        # Agentのアクセスポリシーを追加する
        self.identity_pool.authenticated_role.attach_inline_policy(
            Policy(
                self,
                "AuthPolicy",
                document=PolicyDocument(
                    statements=[
                        PolicyStatement(
                            effect=Effect.ALLOW, actions=["bedrock-agent-runtime:*", "bedrock:*"], resources=["*"]
                        )
                    ]
                ),
            )
        )
        Output(self, "RegionOutput", export_name="Region", value=stack.region)
        Output(self, "UserPoolIdOutput", export_name="CognitoUserPoolId", value=self.user_pool.user_pool_id)
        Output(
            self,
            "ApplicationClientOutput",
            export_name="CognitoApplicationClientId",
            value=self.client.user_pool_client_id,
        )
        Output(
            self,
            "IdentityPoolOutput",
            export_name="CognitoIdentityPoolId",
            value=self.identity_pool.identity_pool_id,
        )
