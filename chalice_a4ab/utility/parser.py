from typing import Type
from chalice import Chalice
from pydantic import BaseModel
from chalice_a4ab.runtime.pydantic_tool.utility import PydanticUtility as u


def read_session_attributes(app: Chalice, session_attribute_key: str, defaults=None):
    """
    Read session attributes from app

    Notice : Can not use in lambda parser function
    """
    try:
        return app.current_request.headers.get(f"session_attributes.{session_attribute_key.lower()}", defaults)
    except Exception:
        return defaults


def read_prompt_session_attributes(app: Chalice, prompt_session_attribute_key: str, defaults=None):
    """
    Read prompt session attributes from app

    Notice : Can not use in lambda parser function
    """
    try:
        return app.current_request.headers.get(
            f"prompt_session_attributes.{prompt_session_attribute_key.lower()}", defaults
        )
    except Exception:
        return defaults


def read_body(app: Chalice, pydantic_model: Type[BaseModel]):
    """
    Read body from app

    Notice : Can not use in lambda parser function
    """
    return u(pydantic_model).parse_obj(app.current_request.json_body)
