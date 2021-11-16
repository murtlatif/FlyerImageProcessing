from dataclasses import dataclass
from enum import Enum


class AnnotationType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


@dataclass
class Vertex:
    x: tuple[int, int]
    y: tuple[int, int]


@dataclass
class OCRAnnotation:
    bounds: list[Vertex]
    text: str
    annotation_type: AnnotationType = None
