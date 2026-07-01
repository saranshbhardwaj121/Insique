from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        return instance

    def list_all(self) -> Sequence[ModelT]:
        raise NotImplementedError("list_all is not safe for all models; use specific queries instead")
