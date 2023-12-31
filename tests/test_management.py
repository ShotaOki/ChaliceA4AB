from chalice_a4ab.cli.management import read_identity
from chalice_a4ab import AgentsForAmazonBedrockConfig


def test_read_identity_default():
    """
    Normaly :: Read Identity by default

    Condition:
        Read identity by default
    Expects:
        Read default identity
    """
    config = AgentsForAmazonBedrockConfig(title="apptst")
    identity = read_identity(
        config,
        session_parameter={},
        default_identity={"UserId": "123456789", "Account": "user_account", "Arn": "xxxxxxxxxx"},
    )
    assert identity.Account == "user_account"
    assert identity.UserId == "123456789"
    assert identity.Arn == "xxxxxxxxxx"
    assert identity.Region == "us-east-1"
    assert identity.lambda_arn == "arn:aws:lambda:us-east-1:user_account:function:apptst-dev"
    assert identity.lambda_function_name == "apptst-dev"
    assert "AmazonBedrockExecutionRoleForAgents_" in identity.agents_role_arn
    assert identity.project_hash in identity.bucket_name
    assert identity.Account in identity.bucket_name


def test_overwrite_identity():
    """
    Normaly :: Read Identity by custom

    Condition:
        Read identity by custom
    Expects:
        Read custom identity
    """
    config = AgentsForAmazonBedrockConfig(title="apptst2")
    identity = read_identity(
        config,
        session_parameter={},
        default_identity={"UserId": "123456789", "Account": "user_account", "Arn": "xxxxxxxxxx"},
        default_region="us-east-2",
        default_stage="prod",
        default_bucket_name="tst-bucket",
        default_lambda_arn="arn:lambda-arn",
    )
    assert identity.Account == "user_account"
    assert identity.UserId == "123456789"
    assert identity.Arn == "xxxxxxxxxx"
    assert identity.Region == "us-east-2"
    assert identity.lambda_arn == "arn:lambda-arn"
    assert identity.lambda_function_name == "lambda-arn"
    assert "AmazonBedrockExecutionRoleForAgents_" in identity.agents_role_arn
    assert identity.bucket_name == "tst-bucket"
