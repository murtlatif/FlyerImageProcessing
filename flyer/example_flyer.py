from util.image_space import Vertex

from .flyer_components import (AdBlock, Flyer, FlyerType, Measurement, Page,
                               PageType, Product, Promotion, PromotionType,
                               Quantity)

EXAMPLE_FLYER = Flyer(
    flyer_type=FlyerType.WEEKLY,
    pages=[
        Page(
            page_type=PageType.MULTI_AD,
            ad_blocks=[
                AdBlock(
                    product=Product(
                        name="Lisa's Lemons",
                        description="The perfect amount of sour.",
                        price=399,
                        quantity=Quantity(
                            measurement=Measurement.unit,
                            amount=4
                        )
                    ),
                    bounds=[
                        Vertex(0, 0),
                        Vertex(0, 100),
                        Vertex(100, 100),
                        Vertex(100, 0),
                    ]
                ),
                AdBlock(
                    product=Product(
                        name="Stephen's Star Fruits",
                        description="But there is no brighter star then Stephen himself.",
                        price=1299,
                        quantity=Quantity(
                            measurement=Measurement.kg,
                            amount=0.3
                        )
                    ),
                    promotion=Promotion(
                        promotion_type=PromotionType.PERCENTAGE,
                        amount=15,
                        promotion_text="15% OFF!",
                    ),
                    bounds=[]
                ),
                AdBlock(
                    product=Product(
                        name="Sandra's Sangria",
                        description="Great for a monday morning.",
                        price=2199,
                        quantity=Quantity(
                            measurement=Measurement.L,
                            amount=1.5
                        )
                    ),
                    promotion=Promotion(
                        promotion_type=PromotionType.BUY_ONE_GET_N_PERCENT_OFF,
                        amount=50,
                        promotion_text='Buy one get one 50% off!'
                    ),
                    bounds=[]
                ),
                AdBlock(
                    product=Product(
                        name="Murtaza's Meat",
                        description="Bones can be removed upon request. Will cut in store if needed.",
                        price=1999,
                        quantity=Quantity(
                            measurement=Measurement.oz,
                            amount=4.3
                        )
                    ),
                    bounds=[]
                ),
            ]
        )
    ]
)

EMPTY_FLYER = Flyer()

EMPTY_PAGE_FLYER = Flyer(
    flyer_type=FlyerType.OTHER,
    pages=[
        Page()
    ]
)
