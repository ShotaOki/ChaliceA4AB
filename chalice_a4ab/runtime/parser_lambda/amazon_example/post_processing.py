import re
import logging

FINAL_RESPONSE_REGEX = r"<final_response>([\s\S]*?)</final_response>"
FINAL_RESPONSE_PATTERN = re.compile(FINAL_RESPONSE_REGEX, re.DOTALL)

logger = logging.getLogger()


# This parser lambda is an example of how to parse the LLM output for the default PostProcessing prompt
def lambda_handler(event, context):
    logger.info("Lambda input: " + str(event))
    raw_response = event["invokeModelRawResponse"]

    parsed_response = {"promptType": "POST_PROCESSING", "postProcessingParsedResponse": {}}

    matcher = FINAL_RESPONSE_PATTERN.search(raw_response)
    if not matcher:
        raise Exception("Could not parse raw LLM output")
    response_text = matcher.group(1).strip()

    parsed_response["postProcessingParsedResponse"]["responseText"] = response_text

    logger.info(parsed_response)
    return parsed_response
