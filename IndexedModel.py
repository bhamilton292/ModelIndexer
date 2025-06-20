from pydantic import BaseModel
from typing import TypeVar, Generic, Callable, Dict, List, Any, Union

GenericModel = TypeVar("GenericModel", bound=BaseModel)

class IndexedModel(Generic[GenericModel]):

    """
    takes a list of models, and a dictionary of key value pairs.
    keys must be unique identifiers.
    """
    def __init__(self, models: List[GenericModel], key_funcs: Dict[str, Callable[[GenericModel], Any]]):
        self._models = models
        self._indexes: Dict[str, Dict[Any, GenericModel]] = {}

        for key_name, func in key_funcs.items():
            index: Dict[Any, GenericModel] = {}
            for model in models:
                key = func(model)
                if key in index:
                    raise ValueError(
                        f"Duplicate key '{key}' found for index '{key_name}' in model {model!r}"
                    )
                index[key] = model
            self._indexes[key_name] = index

    def get(self, key_name: str, key_value: Any) -> Union[GenericModel, None]:
        return self._indexes.get(key_name, {}).get(key_value)

    def all(self) -> List[GenericModel]:
        return self._models

    def index(self, key_name: str) -> Dict[Any, GenericModel]:
        return self._indexes.get(key_name, {})