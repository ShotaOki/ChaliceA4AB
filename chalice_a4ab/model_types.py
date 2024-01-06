from enum import Enum


class ModelTypes(Enum):
    """
    Model types for the Agents.
    """

    CLAUDE_V2 = "anthropic.claude-v2"
    CLAUDE_V2_1 = "anthropic.claude-v2:1"
    CLAUDE_V1_INSTANT = "anthropic.claude-instant-v1"


# Model Defines

# Model Type :: Antrhopic Claude V2
ModelTypesAntropicClaudeV2 = ModelTypes.CLAUDE_V2.value
# Model Type :: Antrhopic Claude V2.1
ModelTypesAntropicClaudeV2_1 = ModelTypes.CLAUDE_V2_1.value
# Model Type :: Antrhopic Claude V1 Instant
ModelTypesAntropicClaudeV1Instant = ModelTypes.CLAUDE_V1_INSTANT.value
