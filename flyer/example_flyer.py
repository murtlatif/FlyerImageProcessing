from .flyer_types import AdBlock, Flyer, FlyerType, Measurement, Page, PageType

EXAMPLE_FLYER = Flyer(
    flyer_type=FlyerType.WEEKLY,
    pages=[
        Page(
            page_type=PageType.MULTI_AD,
            ad_blocks=[
                AdBlock(
                    product_name='Lisa\'s Lemons',
                    product_price=3.99,
                    unit_of_measurement=Measurement.kg
                ),
                AdBlock(
                    product_name='Stephen\'s Sausage',
                    product_price=5.99,
                    unit_of_measurement=Measurement.OTHER
                ),
                AdBlock(
                    product_name='Sandra\'s Sesame Seeds',
                    product_price=4.99,
                    unit_of_measurement=Measurement.kg
                ),
                AdBlock(
                    product_name='Murtaza\'s Meat',
                    product_price=2.99,
                    unit_of_measurement=Measurement.oz
                )
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
