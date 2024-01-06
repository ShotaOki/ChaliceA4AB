import logging
import re
import xml.etree.ElementTree as ET

RATIONALE_REGEX_LIST = ["(.*?)(<function_calls>)", "(.*?)(<answer>)"]
RATIONALE_PATTERNS = [re.compile(regex, re.DOTALL) for regex in RATIONALE_REGEX_LIST]

RATIONALE_VALUE_REGEX_LIST = ["<scratchpad>(.*?)(</scratchpad>)", "(.*?)(</scratchpad>)", "(<scratchpad>)(.*?)"]
RATIONALE_VALUE_PATTERNS = [re.compile(regex, re.DOTALL) for regex in RATIONALE_VALUE_REGEX_LIST]

ANSWER_REGEX = r"(?<=<answer>)(.*)"
ANSWER_PATTERN = re.compile(ANSWER_REGEX, re.DOTALL)

ANSWER_TAG = "<answer>"
FUNCTION_CALL_TAG = "<function_calls>"

ASK_USER_FUNCTION_CALL_REGEX = r"<tool_name>user::askuser</tool_name>"
ASK_USER_FUNCTION_CALL_PATTERN = re.compile(ASK_USER_FUNCTION_CALL_REGEX, re.DOTALL)

ASK_USER_TOOL_NAME_REGEX = r"<tool_name>((.|\n)*?)</tool_name>"
ASK_USER_TOOL_NAME_PATTERN = re.compile(ASK_USER_TOOL_NAME_REGEX, re.DOTALL)

TOOL_PARAMETERS_REGEX = r"<parameters>((.|\n)*?)</parameters>"
TOOL_PARAMETERS_PATTERN = re.compile(TOOL_PARAMETERS_REGEX, re.DOTALL)

ASK_USER_TOOL_PARAMETER_REGEX = r"<question>((.|\n)*?)</question>"
ASK_USER_TOOL_PARAMETER_PATTERN = re.compile(ASK_USER_TOOL_PARAMETER_REGEX, re.DOTALL)


KNOWLEDGE_STORE_SEARCH_ACTION_PREFIX = "x_amz_knowledgebase_"

FUNCTION_CALL_REGEX = r"(?<=<function_calls>)(.*)"

ANSWER_PART_REGEX = "<answer_part\\s?>(.+?)</answer_part\\s?>"
ANSWER_TEXT_PART_REGEX = "<text\\s?>(.+?)</text\\s?>"
ANSWER_REFERENCE_PART_REGEX = "<source\\s?>(.+?)</source\\s?>"
ANSWER_PART_PATTERN = re.compile(ANSWER_PART_REGEX, re.DOTALL)
ANSWER_TEXT_PART_PATTERN = re.compile(ANSWER_TEXT_PART_REGEX, re.DOTALL)
ANSWER_REFERENCE_PART_PATTERN = re.compile(ANSWER_REFERENCE_PART_REGEX, re.DOTALL)

# You can provide messages to reprompt the LLM in case the LLM output is not in the expected format
MISSING_API_INPUT_FOR_USER_REPROMPT_MESSAGE = "Missing the parameter 'question' for user::askuser function call. Please try again with the correct argument added."
ASK_USER_FUNCTION_CALL_STRUCTURE_REMPROMPT_MESSAGE = "The function call format is incorrect. The format for function calls to the askuser function must be: <invoke> <tool_name>user::askuser</tool_name><parameters><question>$QUESTION</question></parameters></invoke>."
FUNCTION_CALL_STRUCTURE_REPROMPT_MESSAGE = "The function call format is incorrect. The format for function calls must be: <invoke> <tool_name>$TOOL_NAME</tool_name> <parameters> <$PARAMETER_NAME>$PARAMETER_VALUE</$PARAMETER_NAME>...</parameters></invoke>."

logger = logging.getLogger()


# This parser lambda is an example of how to parse the LLM output for the default orchestration prompt
def lambda_handler(event, context):
    logger.info("Lambda input: " + str(event))

    # Sanitize LLM response
    sanitized_response = sanitize_response(event["invokeModelRawResponse"])

    # Parse LLM response for any rationale
    rationale = parse_rationale(sanitized_response)

    # Construct response fields common to all invocation types
    parsed_response = {"promptType": "ORCHESTRATION", "orchestrationParsedResponse": {"rationale": rationale}}

    # Check if there is a final answer
    try:
        final_answer, generated_response_parts = parse_answer(sanitized_response)
    except ValueError as e:
        addRepromptResponse(parsed_response, e)
        return parsed_response

    if final_answer:
        parsed_response["orchestrationParsedResponse"]["responseDetails"] = {
            "invocationType": "FINISH",
            "agentFinalResponse": {"responseText": final_answer},
        }

        if generated_response_parts:
            parsed_response["orchestrationParsedResponse"]["responseDetails"]["agentFinalResponse"]["citations"] = {
                "generatedResponseParts": generated_response_parts
            }

        logger.info("Final answer parsed response: " + str(parsed_response))
        return parsed_response

    # Check if there is an ask user
    try:
        ask_user = parse_ask_user(sanitized_response)
        if ask_user:
            parsed_response["orchestrationParsedResponse"]["responseDetails"] = {
                "invocationType": "ASK_USER",
                "agentAskUser": {"responseText": ask_user},
            }

            logger.info("Ask user parsed response: " + str(parsed_response))
            return parsed_response
    except ValueError as e:
        addRepromptResponse(parsed_response, e)
        return parsed_response

    # Check if there is an agent action
    try:
        parsed_response = parse_function_call(sanitized_response, parsed_response)
        logger.info("Function call parsed response: " + str(parsed_response))
        return parsed_response
    except ValueError as e:
        addRepromptResponse(parsed_response, e)
        return parsed_response

    addRepromptResponse(parsed_response, "Failed to parse the LLM output")
    logger.info(parsed_response)
    return parsed_response

    raise Exception("unrecognized prompt type")


def sanitize_response(text):
    pattern = r"(\\n*)"
    text = re.sub(pattern, r"\n", text)
    return text


def parse_rationale(sanitized_response):
    # Checks for strings that are not required for orchestration
    rationale_matcher = next(
        (pattern.search(sanitized_response) for pattern in RATIONALE_PATTERNS if pattern.search(sanitized_response)),
        None,
    )

    if rationale_matcher:
        rationale = rationale_matcher.group(1).strip()

        # Check if there is a formatted rationale that we can parse from the string
        rationale_value_matcher = next(
            (pattern.search(rationale) for pattern in RATIONALE_VALUE_PATTERNS if pattern.search(rationale)), None
        )
        if rationale_value_matcher:
            return rationale_value_matcher.group(1).strip()

        return rationale

    return None


def parse_answer(sanitized_llm_response):
    if has_generated_response(sanitized_llm_response):
        return parse_generated_response(sanitized_llm_response)

    answer_match = ANSWER_PATTERN.search(sanitized_llm_response)
    if answer_match and is_answer(sanitized_llm_response):
        return answer_match.group(0).strip(), None

    return None, None


def is_answer(llm_response):
    return llm_response.rfind(ANSWER_TAG) > llm_response.rfind(FUNCTION_CALL_TAG)


def parse_generated_response(sanitized_llm_response):
    results = []

    for match in ANSWER_PART_PATTERN.finditer(sanitized_llm_response):
        part = match.group(1).strip()

        text_match = ANSWER_TEXT_PART_PATTERN.search(part)
        if not text_match:
            raise ValueError("Could not parse generated response")

        text = text_match.group(1).strip()
        references = parse_references(sanitized_llm_response, part)
        results.append((text, references))

    final_response = " ".join([r[0] for r in results])

    generated_response_parts = []
    for text, references in results:
        generatedResponsePart = {"text": text, "references": references}
        generated_response_parts.append(generatedResponsePart)

    return final_response, generated_response_parts


def has_generated_response(raw_response):
    return ANSWER_PART_PATTERN.search(raw_response) is not None


def parse_references(raw_response, answer_part):
    references = []
    for match in ANSWER_REFERENCE_PART_PATTERN.finditer(answer_part):
        reference = match.group(1).strip()
        references.append({"sourceId": reference})
    return references


def parse_ask_user(sanitized_llm_response):
    ask_user_matcher = ASK_USER_FUNCTION_CALL_PATTERN.search(sanitized_llm_response)
    if ask_user_matcher:
        try:
            parameters_matches = TOOL_PARAMETERS_PATTERN.search(sanitized_llm_response)
            params = parameters_matches.group(1).strip()
            ask_user_question_matcher = ASK_USER_TOOL_PARAMETER_PATTERN.search(params)
            if ask_user_question_matcher:
                ask_user_question = ask_user_question_matcher.group(1)
                return ask_user_question
            raise ValueError(MISSING_API_INPUT_FOR_USER_REPROMPT_MESSAGE)
        except ValueError as ex:
            raise ex
        except Exception as ex:
            raise Exception(ASK_USER_FUNCTION_CALL_STRUCTURE_REMPROMPT_MESSAGE)

    return None


def parse_function_call(sanitized_response, parsed_response):
    match = re.search(FUNCTION_CALL_REGEX, sanitized_response)
    if not match:
        raise ValueError(FUNCTION_CALL_STRUCTURE_REPROMPT_MESSAGE)

    tool_name_matches = ASK_USER_TOOL_NAME_PATTERN.search(sanitized_response)
    tool_name = tool_name_matches.group(1)
    parameters_matches = TOOL_PARAMETERS_PATTERN.search(sanitized_response)
    params = parameters_matches.group(1).strip()

    action_split = tool_name.split("::")
    verb = action_split[0].strip()
    resource_name = action_split[1].strip()
    function = action_split[2].strip()

    xml_tree = ET.ElementTree(ET.fromstring("<parameters>{}</parameters>".format(params)))
    parameters = {}
    for elem in xml_tree.iter():
        if elem.text:
            parameters[elem.tag] = {"value": elem.text.strip('" ')}

    parsed_response["orchestrationParsedResponse"]["responseDetails"] = {}

    # Function calls can either invoke an action group or a knowledge base.
    # Mapping to the correct variable names accordingly
    if resource_name.lower().startswith(KNOWLEDGE_STORE_SEARCH_ACTION_PREFIX):
        parsed_response["orchestrationParsedResponse"]["responseDetails"]["invocationType"] = "KNOWLEDGE_BASE"
        parsed_response["orchestrationParsedResponse"]["responseDetails"]["agentKnowledgeBase"] = {
            "searchQuery": parameters["searchQuery"],
            "knowledgeBaseId": resource_name.replace(KNOWLEDGE_STORE_SEARCH_ACTION_PREFIX, ""),
        }

        return parsed_response

    parsed_response["orchestrationParsedResponse"]["responseDetails"]["invocationType"] = "ACTION_GROUP"
    parsed_response["orchestrationParsedResponse"]["responseDetails"]["actionGroupInvocation"] = {
        "verb": verb,
        "actionGroupName": resource_name,
        "apiName": function,
        "actionGroupInput": parameters,
    }

    return parsed_response


def addRepromptResponse(parsed_response, error):
    error_message = str(error)
    logger.warn(error_message)

    parsed_response["orchestrationParsedResponse"]["parsingErrorDetails"] = {"repromptResponse": error_message}
