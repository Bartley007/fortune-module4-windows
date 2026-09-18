from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy.engine import Dialect
from sqlalchemy.types import JSON, TypeDecorator, TypeEngine


class EmbeddingVector(TypeDecorator[list[float]]):
    """Use pgvector on PostgreSQL and JSON on lightweight SQLite deployments."""

    impl = JSON
    cache_ok = True

    def __init__(self, dimension: int) -> None:
        super().__init__()
        self.dimension = dimension

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(self.dimension))
        return dialect.type_descriptor(JSON())
