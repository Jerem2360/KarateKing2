from typing import Any, Union, Literal


class _Say:

    def __init__(self, value: str):
        self.v = value.split("-say: ")[-1]


Coordinates = tuple[Union[int, float], Union[int, float]]
Direction = Literal["-left", "-right", "-up", "-down"]
Action = Union[Direction, _Say]
RGBColor = tuple[int, int, int]


class Registry:
    Type = object

    def __init__(self, type_: type):
        self.dict = {}
        self.Type = type_
        self._iter_count = 0

    def __getitem__(self, item: str or int):
        if isinstance(item, str):
            return self.dict[item]
        to_count = self._to_list()
        k, v = to_count[item]
        return v

    def __len__(self):
        to_count = self._to_list()
        return len(to_count)

    def __iter__(self):
        self._iter_count = 0
        return self

    def __next__(self) -> tuple[str, Any]:
        if self._iter_count >= len(self):
            raise StopIteration
        to_iter = self._to_list()
        result = to_iter[self._iter_count]
        self._iter_count += 1
        return result

    def _to_list(self) -> list[tuple[str, Any]]:
        result: list[tuple[str, Any]] = []
        for item in self.dict:
            result.append((item, self.dict[item]))
        return result

    def register(self, name: str, value):
        if not isinstance(value, self.Type):
            raise TypeError(f"Incorrect type for provided argument 'value'. Expected type {self.Type}, got {type(value)} instead.")
        self.dict[name] = value

