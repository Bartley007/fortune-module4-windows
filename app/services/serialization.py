from typing import Any, TypeVar, cast

from fastapi.encoders import jsonable_encoder
from sqlalchemy import inspect

T = TypeVar("T")


def model_to_dict(instance: T) -> dict[str, Any]:
    mapper = cast(Any, inspect(instance)).mapper
    data = {column.key: getattr(instance, column.key) for column in mapper.column_attrs}
    return cast(dict[str, Any], jsonable_encoder(data))


def model_list_to_dict(instances: list[T]) -> list[dict[str, Any]]:
    return [model_to_dict(instance) for instance in instances]
