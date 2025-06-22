from pydantic import BaseModel
from typing import TypeVar, Generic, Callable, Dict, List, Any, Union

GenericModel = TypeVar("GenericModel", bound=BaseModel)

class ModelIndex(Generic[GenericModel]):
    """
    Stores and indexes Pydantic models by one or more attribute names (keys).
    Supports fast lookup, addition, and removal of models.
    Keys must be unique across models and across the key list.
    All models must be of the same type.
    """

    def __init__(
        self,
        models: List[GenericModel],
        keys: List[str]
    ):
        if len(set(keys)) != len(keys):
            raise ValueError("Duplicate keys detected in index keys list.")

        self._models: List[GenericModel] = []
        self._indexes: Dict[str, Dict[Any, GenericModel]] = {}
        self._key_funcs = {
            key: self._make_index_key_func(key) for key in keys
        }
        self._model_type = None

        for key in keys:
            self._indexes[key] = {}

        for model in models:
            self.add(model)

    def _make_index_key_func(self, attr_name: str):
        return lambda model: getattr(model, attr_name)

    def add(self, model: GenericModel) -> None:
        """
        Add a model to the collection, update all indexes.
        Raises ValueError on duplicate keys.
        """
        if self._model_type and not isinstance(model, self._model_type):
            raise TypeError(
                f"Expected model of type {self._model_type.__name__}, got {type(model).__name__}"
            )
        elif not self._model_type:
            self._model_type = type(model)

        for key_name, func in self._key_funcs.items():
            key = func(model)
            index = self._indexes[key_name]
            if key in index:
                raise ValueError(f"Duplicate key '{key}' for index '{key_name}' when adding model {model!r}")
            index[key] = model
        self._models.append(model)

    def remove(self, key_name: str, key_value: Any) -> None:
        """
        Remove a model from the collection and all indexes based on a matching key-value pair.
        Raises KeyError if the key-value pair is not present in the collection.
        """
        instance = self.get(key_name, key_value)
        if instance != None:
            self._models.remove(instance)
            for key_name, func in self._key_funcs.items():

                self._indexes[key_name].pop(func(instance))
        else:
            raise KeyError(f"KeyValue Pair (Key:{key_name}; Value: {key_value}) not found in collection.")

    def remove(self, model_or_key: Union[GenericModel, str], key_value: Any = None) -> None:
        """
        Remove a model from the collection.

        Accepts either:
        - A full model instance
        - A (key_name, key_value) pair

        Raises KeyError if the model is not found.
        """
        if isinstance(model_or_key, BaseModel):
            model = model_or_key
        elif isinstance(model_or_key, str) and key_value is not None:
            key_name = model_or_key
            if key_name not in self._indexes:
                raise KeyError(f"Index '{key_name}' does not exist.")
            model = self._indexes[key_name].get(key_value)
            if model is None:
                raise KeyError(f"No model found with {key_name} = {key_value}")
        else:
            raise ValueError("Must provide either a model instance or (key_name, key_value) pair.")

        if model not in self._models:
            raise KeyError(f"Model {model!r} not found in collection.")
        self._models.remove(model)
        for key_name, func in self._key_funcs.items():
            key = func(model)
            self._indexes[key_name].pop(key, None)

    def get(self, key_name: str, key_value: Any) -> Union[GenericModel, None]:
        return self._indexes.get(key_name, {}).get(key_value)

    def all(self) -> List[GenericModel]:
        return list(self._models)

    def index(self, key_name: str) -> Dict[Any, GenericModel]:
        return dict(self._indexes.get(key_name, {}))
