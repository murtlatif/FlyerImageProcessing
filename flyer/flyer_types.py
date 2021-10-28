from dataclasses import dataclass
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
    product_name: str
    product_price: float
    unit_of_measurement: Measurement


@dataclass
class Page:
    page_type: PageType
    ad_blocks: list[AdBlock]


@dataclass
class Flyer:
    flyer_type: FlyerType
    pages: list[Page]
