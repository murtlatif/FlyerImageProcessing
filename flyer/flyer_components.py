from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from util.image_space import Region


class StringValueEnum(str, Enum):
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}.{self.name}>'


class Measurement(StringValueEnum):
    lb = 'lb'
    lbs = 'lbs'
    oz = 'oz'
    kg = 'kg'
    mL = 'ml'
    g = 'g'
    L = 'l'
    unit = 'unit'

    @staticmethod
    def valid_measurements() -> list[str]:
        """
        Gets a list of valid measurements strings.

        Returns:
            list[str]: Valid measurement strings
        """
        measurements = [measurement.value for measurement in Measurement]
        return measurements


class PageType(StringValueEnum):
    MULTI_AD = 'multi-ad'
    OTHER = 'other'


class FlyerType(StringValueEnum):
    WEEKLY = 'weekly'
    OTHER = 'other'


class PromotionType(StringValueEnum):
    PERCENTAGE = 'percentage'
    FLAT = 'flat'
    BUY_N_GET_ONE_FREE = 'buy-N-get-one-free'
    BUY_ONE_GET_N_PERCENT_OFF = 'buy-one-get-N-percent-off'
    BUY_ONE_GET_N_AMOUNT_OFF = 'buy-one-get-N-amount-off'


class AdBlockComponentType(Enum):
    UNKNOWN = auto()
    PRODUCT_NAME = auto()
    PRODUCT_DESCRIPTION = auto()
    PRODUCT_PRICE = auto()
    PRODUCT_CODE = auto()
    PRODUCT_PRICE_UNIT = auto()
    QUANTITY = auto()
    PROMOTION = auto()


@dataclass
class AdBlockComponent:
    component_type: AdBlockComponentType
    value: Any
    bounds: Region


@dataclass
class Quantity():
    measurement: Measurement
    text: str
    amount: float = None


@dataclass
class Promotion():
    promotion_type: PromotionType
    amount: float
    promotion_text: str


@dataclass
class Product:
    name: str = None
    description: str = None
    code: str = None
    price: int = None
    price_unit: str = None
    quantity: Quantity = field(default_factory=Quantity)


@dataclass
class AdBlock:
    product: Product = field(default_factory=Product)
    promotion: Promotion = None
    bounds: Region = field(default_factory=list)
    additional_data: str = None


@dataclass
class Page:
    page_type: PageType = None
    ad_blocks: list[AdBlock] = field(default_factory=list)


@dataclass
class Flyer:
    flyer_type: FlyerType = None
    pages: list[Page] = field(default_factory=list)
