from typing import Any


class PydanticUtility:
    """
    Support Pydantic v1 and v2 Wrapper
    """

    _model: Any

    def __init__(self, model: Any) -> None:
        """
        input Pydantic BaseModel Class

        :param model: Pydantic BaseModel Class
        """
        self._model = model

    def parse_obj(self, obj: Any):
        """
        Parse object to Pydantic Model
        """
        if hasattr(self._model, "model_validate"):
            return self._model.model_validate(obj)
        else:
            return self._model.parse_obj(obj)

    def dict(self, *args, **kwargs):
        """
        Object to dict
        """
        if hasattr(self._model, "model_dump"):
            return self._model.model_dump(*args, **kwargs)
        else:
            return self._model.dict(*args, **kwargs)

    def json(self, *args, **kwargs):
        """
        Object to json
        """
        if hasattr(self._model, "model_dump_json"):
            return self._model.model_dump_json(*args, **kwargs)
        else:
            return self._model.json(*args, **kwargs)
