from typing import NamedTuple, Sequence


class Vertex(NamedTuple):
    x: tuple[int, int]
    y: tuple[int, int]


class OCRAnnotation(NamedTuple):
    bounds: Sequence[Vertex]
    text: str
