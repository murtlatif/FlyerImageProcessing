from collections import defaultdict
from typing import Any
from ocr.get_annotations import find_annotations_in_region

from flyer.flyer_components import (AdBlock, AdBlockComponent,
                                    AdBlockComponentType, Flyer, FlyerType,
                                    Page, PageType, Product)
from util.image_space import Vertex, distance_between_regions, Region

from .annotation_types import HierarchicalAnnotation
from .ocr_flyer_analysis import extract_component_from_block


def process_page_annotation(page_annotation: HierarchicalAnnotation) -> Page:
    """
    Use a Page level HierarchicalAnnotation to extract the ad blocks
    shown on the page. The ad blocks and additional data are used to
    compile a Page object.

    Args:
        page_annotation (HierarchicalAnnotation): Annotation for the page

    Returns:
        Page: A page object containing the ad blocks on the page
    """
    ad_block_components: dict[AdBlockComponentType, list[AdBlockComponent]] = defaultdict(list)

    # Process each block annotation into an Ad Block Component
    for block_annotation in page_annotation.child_annotations:
        ad_block_component = extract_component_from_block(block_annotation)
        ad_block_components[ad_block_component.component_type].append(ad_block_component)

    ad_blocks = construct_ad_blocks_from_components(ad_block_components)

    page_type = PageType.MULTI_AD if len(ad_blocks) > 1 else PageType.OTHER
    page = Page(page_type=page_type, ad_blocks=ad_blocks)

    return page


def process_flyer_annotation(page_annotations: list[HierarchicalAnnotation]) -> Flyer:
    """
    Processes a list of page annotations into a flyer object.

    Args:
        page_annotations (list[HierarchicalAnnotation]): Page annotations

    Returns:
        Flyer: Compiled flyer object
    """
    pages: list[Page] = []

    for page_annotation in page_annotations:
        page = process_page_annotation(page_annotation)
        pages.append(page)

    # TODO: Add logic to get flyer type
    flyer_type = FlyerType.WEEKLY
    flyer = Flyer(
        flyer_type=flyer_type,
        pages=pages
    )

    return flyer


def process_segmented_page_annotation(page_annotation: HierarchicalAnnotation, page_segmentation: list[Region]):

    ad_blocks: list[AdBlock] = []

    # Create an ad block for each segment
    for segment_bounds in page_segmentation:

        ad_block_components: defaultdict[AdBlockComponentType, list[AdBlockComponent]] = defaultdict(list)
        # Get all block annotations in the segmented block
        block_annotations = find_annotations_in_region(page_annotation.child_annotations, segment_bounds)

        for block_annotation in block_annotations:
            ad_block_component = extract_component_from_block(block_annotation)
            ad_block_components[ad_block_component.component_type].append(ad_block_component)

        ad_block = construct_segmented_block_from_components(ad_block_components)
        ad_blocks.append(ad_block)

    page_type = PageType.MULTI_AD if len(ad_blocks) > 1 else PageType.OTHER
    page = Page(page_type=page_type, ad_blocks=ad_blocks)

    return page


def construct_segmented_block_from_components(components: defaultdict[AdBlockComponentType, list[AdBlockComponent]]) -> AdBlock:

    product_names = components[AdBlockComponentType.PRODUCT_NAME]
    product_prices = components[AdBlockComponentType.PRODUCT_DESCRIPTION]
    product_prices = components[AdBlockComponentType.PRODUCT_PRICE]
    product_prices = components[AdBlockComponentType.QUANTITY]

    if len(product_names) > 0:
        product_name = _get_component_value(product_names[0])

    if len(product_prices) > 0:
        product_price = _get_component_value(product_prices[0])

    # TODO: CONTINUE FIXING THIS!
    product_description = _get_component_value(nearest_components[AdBlockComponentType.PRODUCT_DESCRIPTION])
    product_price = _get_component_value(price_component)
    product_price_unit = _get_component_value(nearest_components[AdBlockComponentType.PRODUCT_PRICE_UNIT])
    quantity = _get_component_value(nearest_components[AdBlockComponentType.QUANTITY])

    product = Product(
        name=product_name,
        description=product_description,
        price=product_price,
        price_unit=product_price_unit,
        quantity=quantity
    )

    promotion = _get_component_value(nearest_components[AdBlockComponentType.PROMOTION])

    bounding_components = [price_component] + \
        [component for component in nearest_components.values() if component is not None]
    ad_block_bounds = get_component_group_bounds(bounding_components)
    ad_block = AdBlock(product=product, promotion=promotion, bounds=ad_block_bounds)
    ad_block.append(ad_block)

    return ad_block


def process_segmented_flyer_annotations(page_annotations: list[HierarchicalAnnotation], page_segmentations: list[list[Region]]) -> Flyer:
    pages: list[Page] = []

    for page_annotation, page_segmentation in zip(page_annotations, page_segmentations):
        page = process_segmented_page_annotation(page_annotation, page_segmentation)
        pages.append(page)

    # TODO: Add logic to get flyer type
    flyer_type = FlyerType.WEEKLY
    flyer = Flyer(
        flyer_type=flyer_type,
        pages=pages
    )

    return flyer


def construct_ad_blocks_from_components(components: defaultdict[AdBlockComponentType, list[AdBlockComponent]]) -> list[AdBlock]:
    ad_blocks: list[AdBlock] = []

    for price_component in components[AdBlockComponentType.PRODUCT_PRICE]:
        nearest_components: dict[AdBlockComponentType, AdBlockComponent] = {}
        # Take closest components and group them into an ad block
        for component_type in AdBlockComponentType:
            # Skip UNKNOWN and PRODUCT_PRICE components
            if component_type == AdBlockComponentType.UNKNOWN or component_type == AdBlockComponentType.PRODUCT_PRICE:
                continue

            nearest_component = get_nearest_component(price_component, components[component_type])
            nearest_components[component_type] = nearest_component

        product_name = _get_component_value(nearest_components[AdBlockComponentType.PRODUCT_NAME])
        product_description = _get_component_value(nearest_components[AdBlockComponentType.PRODUCT_DESCRIPTION])
        product_price = _get_component_value(price_component)
        product_price_unit = _get_component_value(nearest_components[AdBlockComponentType.PRODUCT_PRICE_UNIT])
        quantity = _get_component_value(nearest_components[AdBlockComponentType.QUANTITY])

        product = Product(
            name=product_name,
            description=product_description,
            price=product_price,
            price_unit=product_price_unit,
            quantity=quantity
        )

        promotion = _get_component_value(nearest_components[AdBlockComponentType.PROMOTION])

        bounding_components = [price_component] + \
            [component for component in nearest_components.values() if component is not None]
        ad_block_bounds = get_component_group_bounds(bounding_components)
        ad_block = AdBlock(product=product, promotion=promotion, bounds=ad_block_bounds)
        ad_blocks.append(ad_block)

    return ad_blocks


def get_nearest_component(from_component: AdBlockComponent, component_list: list[AdBlockComponent]):
    nearest_component = None
    minimum_distance = float('inf')
    for to_component in component_list:
        distance_between_components = distance_between_regions(from_component.bounds, to_component.bounds)
        if distance_between_components < minimum_distance:
            nearest_component = to_component
            minimum_distance = distance_between_components

    return nearest_component


def get_component_group_bounds(components: list[AdBlockComponent]) -> Region:
    all_vertices = [vertex for component in components for vertex in component.bounds]
    x_values = [vertex.x for vertex in all_vertices]
    y_values = [vertex.y for vertex in all_vertices]

    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)

    group_bounds = [
        Vertex(min_x, min_y),
        Vertex(min_x, max_y),
        Vertex(max_x, max_y),
        Vertex(max_x, min_y),
    ]

    return group_bounds


def _get_component_value(component: 'AdBlockComponent | None') -> Any:
    if component is None:
        return None

    return component.value
