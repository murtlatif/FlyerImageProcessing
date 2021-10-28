from dataclasses import dataclass, field
from enum import Enum


class StringValueEnum(str, Enum):
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}.{self.name}>'


class Measurement(StringValueEnum):
    lb = 'lb'
    oz = 'oz'
    kg = 'kg'
    ml = 'ml'
    g = 'g'
    OTHER = 'other'

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}.{self.name}>'


class PageType(StringValueEnum):
    MULTI_AD = 'multi-ad'
    OTHER = 'other'


class FlyerType(StringValueEnum):
    WEEKLY = 'weekly'
    OTHER = 'other'


@dataclass
class AdBlock:
    product_name: str = None
    product_price: float = None
    unit_of_measurement: Measurement = None


@dataclass
class Page:
    page_type: PageType = None
    ad_blocks: list[AdBlock] = field(default_factory=list)


@dataclass
class Flyer:
    flyer_type: FlyerType = None
    pages: list[Page] = field(default_factory=list)
