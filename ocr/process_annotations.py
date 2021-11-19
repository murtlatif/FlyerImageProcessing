from collections import defaultdict
from typing import Any

from flyer.flyer_components import (AdBlock, AdBlockComponent,
                                    AdBlockComponentType, Flyer, FlyerType,
                                    Page, PageType, Product)
from util.image_space import Vertex, distance_between_regions

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
        print(f'Extracting ad block component from block annotation. Got: {ad_block_component}')
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


def construct_ad_blocks_from_components(components: dict[AdBlockComponentType, list[AdBlockComponent]]) -> list[AdBlock]:
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
        quantity = _get_component_value(nearest_components[AdBlockComponentType.QUANTITY])

        product = Product(
            name=product_name,
            description=product_description,
            price=product_price,
            quantity=quantity
        )

        promotion = _get_component_value(nearest_components[AdBlockComponentType.PROMOTION])

        bounding_components = [price_component] + [component for component in nearest_components.values() if component is not None]
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


def get_component_group_bounds(components: list[AdBlockComponent]) -> list[Vertex]:
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
