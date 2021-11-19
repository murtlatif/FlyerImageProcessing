from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from util.image_space import Region


class AnnotationLevel(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


@dataclass
class Annotation:
    bounds: Region
    text: str


@dataclass
class HierarchicalAnnotation(Annotation):
    annotation_level: AnnotationLevel = None
    child_annotations: list[Annotation] = field(default_factory=list)
