from typing import Generic, TypeVar

ReturnT = TypeVar("ReturnT")


class AbstractSource(Generic[ReturnT]):
    def __iter__(self):
        return self

    def __next__(self) -> ReturnT:
        return ReturnT()


class UniqueSourceDecorator(AbstractSource[ReturnT]):
    __slots__ = ["_wrappe", "_cache"]

    def __init__(self, wrapee: AbstractSource[ReturnT]) -> None:
        super().__init__()

        self._wrappe = wrapee
        self._cache: set[ReturnT] = set[ReturnT]()

    def __bool__(self):
        return bool(self._wrappe)

    def __next__(self) -> ReturnT:
        result = next(self._wrappe)
        while result in self._cache:
            result = next(self._wrappe)

        self._cache.add(result)

        return result


class NotEmptySourceDecorator(AbstractSource[ReturnT]):
    __slots__ = ["_wrappe"]

    def __init__(self, wrapee: AbstractSource[ReturnT]) -> None:
        super().__init__()

        self._wrappe = wrapee

    def __bool__(self):
        return bool(self._wrappe)

    def __next__(self) -> ReturnT:
        result = next(self._wrappe)
        while len(result) == 0:
            result = next(self._wrappe)

        return result


__all__ = [
    "AbstractSource",
    "NotEmptySourceDecorator",
    "ReturnT",
    "UniqueSourceDecorator",
    "unique_decorator",
    "not_empty_decorator",
]
