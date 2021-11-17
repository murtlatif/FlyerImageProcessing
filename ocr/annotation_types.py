from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AnnotationLevel(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


@dataclass
class Vertex:
    x: int
    y: int

    @staticmethod
    def from_dict(vertex_dict: dict[str, int]) -> Vertex:
        return Vertex(x=vertex_dict.x, y=vertex_dict.y)


@dataclass
class Annotation:
    bounds: list[Vertex]
    text: str


@dataclass
class HierarchicalAnnotation(Annotation):
    annotation_level: AnnotationLevel = None
    child_annotations: list[Annotation] = field(default_factory=list)
