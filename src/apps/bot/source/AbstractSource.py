from typing import Generic, TypeVar

ReturnT = TypeVar("ReturnT")


class AbstractUniqueSource(Generic[ReturnT]):
    __slots__ = ["__source_holder"]

    def __init__(self) -> None:
        self.__source_holder = set[ReturnT]()

    def _hold(self, item: ReturnT) -> None:
        self.__source_holder.add(item)

    def _has_value(self, value: ReturnT) -> bool:
        return value in self.__source_holder

    def _reset(self) -> None:
        self.__source_holder.clear()

    def __iter__(self):
        return self

    def __next__(self) -> ReturnT:
        return ReturnT()


__all__ = ["AbstractUniqueSource", "ReturnT"]
