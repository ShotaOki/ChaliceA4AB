import time
import boto3
from pydantic import BaseModel, Field
from hashlib import md5
import io
from chalice_a4ab.cli.agent_model import AgentModelEditable, AgentModelReadonly
from chalice_a4ab.runtime.models.parser_lambda import PromptType
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u
from chalice_a4ab import AgentsForAmazonBedrockConfig


class CallerIdentity(BaseModel):
    UserId: str
    Account: str
    Arn: str
    Region: str
    AgentConfig: AgentsForAmazonBedrockConfig
    DefaultBucketName: str = Field("")
    Stage: str = Field("dev")

    @property
    def session(self):
        return boto3.Session(region_name=self.Region)

    @property
    def bucket_name(self):
        if len(self.DefaultBucketName) >= 1:
            return self.DefaultBucketName
        return f"agents-for-bedrock-{self.Account}-{self.project_hash}"

    @property
    def lambda_arn(self):
        return f"arn:aws:lambda:{self.Region}:{self.Account}:function:{self.lambda_function_name}"

    @property
    def lambda_function_name(self):
        return f"{self.AgentConfig.title}-{self.Stage}"

    @property
    def agents_role_arn(self):
        return f"arn:aws:iam::{self.Account}:role/AmazonBedrockExecutionRoleForAgents_{self.project_hash}"

    @property
    def project_hash(self):
        return md5(self.AgentConfig.title.encode("utf-8")).hexdigest()[:8]

    @property
    def stack_name(self):
        return f"{self.AgentConfig.title}_stack".replace("_", "")

    def agent_id_to_arn(self, agent_id: str):
        return f"arn:aws:bedrock:{self.Region}:{self.Account}:agent/{agent_id}"


def read_identity(
    agent_config: AgentsForAmazonBedrockConfig,
    region: str = "us-east-1",
    profile: str = "default",
    bucket_name: str = "",
):
    """
    Read Account Identity from STS
    """
    # Create Session on Current Region
    session = boto3.Session(region_name=region, profile_name=profile)
    # Get Account Into
    identity = session.client("sts").get_caller_identity()
    # Set Region
    identity["Region"] = region
    # Set Identity Config
    identity["AgentConfig"] = agent_config
    # Set Bucket Name
    identity["DefaultBucketName"] = bucket_name
    # Parse with pydantic
    item = u(CallerIdentity).parse_obj(identity)
    # Return Identity
    return item


class CurrentAgentInfo(BaseModel):
    """
    Agents for Amazon Bedrock Response Value
    """

    # Agent Id
    agent_id: str
    # Action Group Id
    action_group_id: str
    # Agent Status
    agent_status: str


def read_current_agent_info(identity: CallerIdentity, bedrock_agent) -> CurrentAgentInfo:
    """
    Read Current Agent Info From AWS Cloud
    """
    # Get Agent Id
    agent_ids = [
        {
            "id": item["agentId"],  # Search Agent Id from Agent Name
            "status": item["agentStatus"],  # Search Agent Status from Agent Name
        }
        for item in bedrock_agent.list_agents()["agentSummaries"]
        if item["agentName"] == identity.AgentConfig.title
    ]
    if len(agent_ids) == 0:
        # No Agent id: Abort process
        print("not found agent")
        return None

    # Get Action Group Id
    action_group_ids = [
        item["actionGroupId"]  # Search Action Group Id from Action Group Name
        for item in bedrock_agent.list_agent_action_groups(
            agentId=agent_ids[0]["id"], agentVersion=identity.AgentConfig.agent_version
        )["actionGroupSummaries"]
        if item["actionGroupName"] == identity.AgentConfig.agent_action_name
    ]
    if len(action_group_ids) == 0:
        return CurrentAgentInfo(
            agent_id=agent_ids[0]["id"],
            agent_status=agent_ids[0]["status"],
            action_group_id="",
        )

    return CurrentAgentInfo(
        agent_id=agent_ids[0]["id"],
        agent_status=agent_ids[0]["status"],
        action_group_id=action_group_ids[0],
    )


def read_user_input_action(identity: CallerIdentity, bedrock_agent) -> CurrentAgentInfo:
    """
    Read Current Agent Info From AWS Cloud
    """
    # Get Agent Id
    agent_ids = [
        {
            "id": item["agentId"],  # Search Agent Id from Agent Name
            "status": item["agentStatus"],  # Search Agent Status from Agent Name
        }
        for item in bedrock_agent.list_agents()["agentSummaries"]
        if item["agentName"] == identity.AgentConfig.title
    ]
    if len(agent_ids) == 0:
        # No Agent id: Abort process
        print("not found agent")
        return None
    # Get Action Group Id
    action_group_ids = [
        item["actionGroupId"]  # Search Action Group Id from Action Group Name
        for item in bedrock_agent.list_agent_action_groups(
            agentId=agent_ids[0]["id"], agentVersion=identity.AgentConfig.agent_version
        )["actionGroupSummaries"]
        if item["actionGroupName"] == "UserInputAction"
    ]
    if len(action_group_ids) == 0:
        print("not found User Input Action group")
        return None
    return CurrentAgentInfo(
        agent_id=agent_ids[0]["id"],
        agent_status=agent_ids[0]["status"],
        action_group_id=action_group_ids[0],
    )


def create_resource(template_file: str, identity: CallerIdentity, cfn):
    """
    Create Resource for Agent with CloudFormation
    """
    # Read Cloudformation template
    with open(template_file) as fp:
        template_body = fp.read()

    # Create Stack parameter
    # Required "Capability Named IAM"
    parameter = {
        "StackName": identity.stack_name,
        "TemplateBody": template_body,
        "Capabilities": ["CAPABILITY_NAMED_IAM"],
        "Parameters": [
            {"ParameterKey": "HashCode", "ParameterValue": identity.project_hash},
        ],
    }

    try:
        # Create Resources
        cfn.create_stack(**parameter)
    except Exception:
        # Update Resources
        cfn.update_stack(**parameter)


def get_agent_info(bedrock_agent, agent_id: str):
    response = bedrock_agent.get_agent(agentId=agent_id)
    agent_editable: AgentModelEditable = u(AgentModelEditable).parse_obj(response["agent"])
    agent_readonly: AgentModelReadonly = u(AgentModelReadonly).parse_obj(response["agent"])
    return (agent_editable, agent_readonly)


def update_editable_agent_with_override_lambda(
    identity: CallerIdentity, config: AgentsForAmazonBedrockConfig, editable_agent: AgentModelEditable
):
    # Parser Lambda Setting
    for type in [
        PromptType.PRE_PROCESSING,
        PromptType.ORCHESTRATION,
        PromptType.POST_PROCESSING,
        PromptType.KNOWLEDGE_BASE_RESPONSE_GENERATION,
    ]:
        if type in config._enabled_prompt_type_list:
            editable_agent.set_enable_configration(type, True)
        else:
            editable_agent.set_enable_configration(type, False)
    if len(config._enabled_prompt_type_list) >= 1:
        editable_agent.prompt_override_configuration.override_lambda = identity.lambda_arn


def init(identity: CallerIdentity, config: AgentsForAmazonBedrockConfig, template_path: str):
    """
    Command : init

    Create Initial Resource
    """
    # Create CloudFormation Client
    cfn = identity.session.client("cloudformation")

    print("Start : Init")

    # Create Cloudfomation Stack
    create_resource(template_path, identity, cfn)
    print(f"- Created stack : {identity.stack_name}")

    # Wait for complete
    waiter = cfn.get_waiter("stack_create_complete")
    waiter.wait(StackName=identity.stack_name)

    # Upload OpenAPI Schema File
    bucket = identity.session.resource("s3").Bucket(identity.bucket_name)
    with io.BytesIO(config.agents_for_bedrock_schema_json().encode("utf-8")) as fp:
        bucket.upload_fileobj(fp, identity.AgentConfig.schema_file)
    print(f"- Uploaded OpenAPI schema file to {identity.bucket_name}/{identity.AgentConfig.schema_file}")

    # Create Agent for Amazon Bedrock
    bedrock_agent = identity.session.client("bedrock-agent")
    response = bedrock_agent.create_agent(
        agentName=identity.AgentConfig.title,
        agentResourceRoleArn=identity.agents_role_arn,
        instruction=identity.AgentConfig.instructions,
        description=identity.AgentConfig.description,
        idleSessionTTLInSeconds=identity.AgentConfig.idle_session_ttl_in_seconds,
        foundationModel=identity.AgentConfig.foundation_model,
    )

    # Get Created Agent Id
    agent_id = response["agent"]["agentId"]
    print(f"- Created agents for amazon bedrock : {agent_id}")

    # Wait for creating agent
    while True:
        current_agent = read_current_agent_info(identity, bedrock_agent)
        if current_agent is None:
            print("Failed to create agent")
            return
        if current_agent.agent_status == "CREATING":
            time.sleep(5)
        else:
            # Success to create agent
            break

    # Get Current Agent
    editable_agent, readonly_agent = get_agent_info(bedrock_agent, agent_id)
    update_editable_agent_with_override_lambda(identity, config, editable_agent)
    # Apply Status
    bedrock_agent.update_agent(**u(editable_agent).dict(by_alias=True, exclude_none=True))

    # Create Agent Action Group
    bedrock_agent.create_agent_action_group(
        agentId=agent_id,
        agentVersion=identity.AgentConfig.agent_version,
        actionGroupName=identity.AgentConfig.agent_action_name,
        description=identity.AgentConfig.description,
        actionGroupExecutor={"lambda": identity.lambda_arn},
        apiSchema={
            "s3": {
                "s3BucketName": identity.bucket_name,
                "s3ObjectKey": identity.AgentConfig.schema_file,
            }
        },
        actionGroupState="ENABLED",
    )
    print("- Created agent action group")

    # Read Action
    action = read_user_input_action(identity, bedrock_agent)
    user_input_enable_parameter = {
        "agentId": agent_id,
        "agentVersion": identity.AgentConfig.agent_version,
        "actionGroupName": "UserInputAction",
        "actionGroupState": "ENABLED",
        "parentActionGroupSignature": "AMAZON.UserInput",
    }
    if action is not None:
        user_input_enable_parameter["actionGroupId"] = action.action_group_id
        # Enable User Input.
        bedrock_agent.update_agent_action_group(**user_input_enable_parameter)
    else:
        # Enabel User Input.(Create)
        bedrock_agent.create_agent_action_group(**user_input_enable_parameter)
    print("- Enabled UserInputAction")

    response = bedrock_agent.prepare_agent(
        agentId=agent_id,
    )
    print("- Prepared agent")

    # Add Permission to Lambda Function for Execute from Agent
    identity.session.client("lambda").add_permission(
        Action="lambda:InvokeFunction",
        FunctionName=identity.lambda_function_name,
        Principal="bedrock.amazonaws.com",
        SourceArn=identity.agent_id_to_arn(agent_id),
        StatementId="amazon-bedrock-agent",
    )
    print(f"- Added permission to lambda function : {identity.lambda_function_name}")

    # Finished Message
    print("completed")


def sync(identity: CallerIdentity, config: AgentsForAmazonBedrockConfig, template_path: str):
    """
    Command : sync

    Sync local LLM Message to cloud.
    """
    # Create Agent for Amazon Bedrock Client
    bedrock_agent = identity.session.client("bedrock-agent")

    print("Start : Sync")

    # Upload OpenAPI Schema File
    bucket = identity.session.resource("s3").Bucket(identity.bucket_name)
    with io.BytesIO(config.agents_for_bedrock_schema_json().encode("utf-8")) as fp:
        bucket.upload_fileobj(fp, identity.AgentConfig.schema_file)
    print(f"- Uploaded OpenAPI schema file to {identity.bucket_name}/{identity.AgentConfig.schema_file}")

    # Get Current Agent Setting
    agent_info = read_current_agent_info(identity, bedrock_agent)
    if (agent_info is None) or len(agent_info.action_group_id) == 0:
        print("not found agent")
        return

    # Get Current Agent
    editable_agent, readonly_agent = get_agent_info(bedrock_agent, agent_info.agent_id)
    editable_agent.instruction = identity.AgentConfig.instructions
    editable_agent.foundation_model = identity.AgentConfig.foundation_model
    editable_agent.description = identity.AgentConfig.description
    editable_agent.idle_session_ttl_in_seconds = identity.AgentConfig.idle_session_ttl_in_seconds
    editable_agent.agent_resource_role_arn = identity.agents_role_arn
    update_editable_agent_with_override_lambda(identity, config, editable_agent)
    # Apply Status
    bedrock_agent.update_agent(**u(editable_agent).dict(by_alias=True, exclude_none=True))

    # Get Current Agent Action Group
    response = bedrock_agent.get_agent_action_group(
        agentId=agent_info.agent_id,
        agentVersion=identity.AgentConfig.agent_version,
        actionGroupId=agent_info.action_group_id,
    )
    print(f"- Get current agent : {agent_info.agent_id} : {agent_info.action_group_id}")

    # Rewrite Agent, sync current setting.
    bedrock_agent.update_agent_action_group(
        agentId=agent_info.agent_id,
        agentVersion=response["agentActionGroup"]["agentVersion"],
        actionGroupId=response["agentActionGroup"]["actionGroupId"],
        actionGroupName=response["agentActionGroup"]["actionGroupName"],
        description=identity.AgentConfig.description,
        actionGroupExecutor={"lambda": response["agentActionGroup"]["actionGroupExecutor"]["lambda"]},
        actionGroupState="ENABLED",
        apiSchema={
            "s3": {
                "s3BucketName": response["agentActionGroup"]["apiSchema"]["s3"]["s3BucketName"],
                "s3ObjectKey": response["agentActionGroup"]["apiSchema"]["s3"]["s3ObjectKey"],
            }
        },
    )
    print(f"- Updated agents for amazon bedrock : {agent_info.agent_id}")

    response = bedrock_agent.prepare_agent(
        agentId=agent_info.agent_id,
    )
    print("- Prepared agent")

    # Finished Message
    print("completed")


def delete(identity: CallerIdentity, config: AgentsForAmazonBedrockConfig, template_path: str):
    """
    Command : delete

    Delete Agent for Amazon Bedrock Resources
    """

    # Create Agent for Amazon Bedrock Client and S3 Client
    bedrock_agent = identity.session.client("bedrock-agent")
    s3 = identity.session.client("s3")

    print("Start : Delete")

    try:
        # Delete OpenAPI Schema File
        s3.delete_object(Bucket=identity.bucket_name, Key=identity.AgentConfig.schema_file)
        print(f"- Deleted OpenAPI schema file to {identity.bucket_name}/{identity.AgentConfig.schema_file}")
    except Exception:
        print("- Delete Failed : OpenAPI schema file")

    try:
        # Get Current Agent Setting
        agent_info = read_current_agent_info(identity, bedrock_agent)
        if (agent_info is None) or len(agent_info.action_group_id) == 0:
            print("not found agent")
            raise Exception("not found agent")

        try:
            # Delete Agent Action Group
            bedrock_agent.delete_agent_action_group(
                agentId=agent_info.agent_id,
                agentVersion=identity.AgentConfig.agent_version,
                actionGroupId=agent_info.action_group_id,
                skipResourceInUseCheck=True,
            )
            print("- Deleted agent action group")
        except Exception:
            print("- Delete Failed : Agent Action Group")

        # Delete Agent
        bedrock_agent.delete_agent(agentId=agent_info.agent_id, skipResourceInUseCheck=True)
        print(f"- Deleted agents for amazon bedrock : {agent_info.agent_id}")
    except Exception:
        print("- Delete Failed : Agent")

    try:
        # Delete CloudFormation Stack
        cfn = identity.session.client("cloudformation")
        cfn.delete_stack(StackName=identity.stack_name)
        print(f"- Start to delete stack... : {identity.stack_name}")

        # Wait for complete
        waiter = cfn.get_waiter("stack_delete_complete")
        waiter.wait(StackName=identity.stack_name)
        print(f"- Deleted stack : {identity.stack_name}")
    except Exception:
        print("- Delete Failed : CloudFormation Stack")

    # Finished Message
    print("completed")


def show(config: AgentsForAmazonBedrockConfig):
    """
    Show OpenAPI Document
    """
    print(config.agents_for_bedrock_schema_json())
