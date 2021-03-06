import re
from collections import defaultdict
from typing import Any

from flyer.flyer_components import (AdBlock, AdBlockComponent,
                                    AdBlockComponentType, CategoryPrediction,
                                    Flyer, FlyerType, Page, PageType, Product)
from product_classification_data import product_classifier
from util.constants import HOLIDAY_WORD_LIST
from util.image_space import (Region, Vertex, distance_between_regions,
                              get_region_area)

from ocr.get_annotations import find_annotations_in_region

from .annotation_types import HierarchicalAnnotation
from .ocr_flyer_analysis import extract_components_from_block


def construct_flyer_from_pages(pages: list[Page], flyer_name: str) -> Flyer:
    """
    TODO: Implement extraction of date by doing regex search of dates within
    page annotation texts.

    Creates a Flyer object from a list of Pages.
    """
    flyer_type = FlyerType.WEEKLY
    for page in pages:
        if page.has_holiday_content:
            flyer_type = FlyerType.HOLIDAY
            break

    flyer = Flyer(
        flyer_type=flyer_type,
        flyer_name=flyer_name,
        flyer_date=None,
        num_pages=len(pages),
        pages=pages
    )
    return flyer


def construct_page_from_ad_blocks(page_number: int, page_file_name: str, ad_blocks: list[AdBlock], page_annotation: HierarchicalAnnotation) -> Page:
    """
    Creates a Page object from a list of AdBlocks.
    """
    page_type = PageType.MULTI_AD if len(ad_blocks) > 1 else PageType.OTHER

    has_holiday_content = contains_holiday_text(page_annotation.text)
    page = Page(
        page_number=page_number,
        page_file_name=page_file_name,
        page_type=page_type,
        num_ad_blocks=len(ad_blocks),
        ad_blocks=ad_blocks,
        has_holiday_content=has_holiday_content,
    )

    return page


def process_page_annotation(page_number: int, page_file_name: str, page_annotation: HierarchicalAnnotation) -> Page:
    """
    Use a Page level HierarchicalAnnotation to extract the ad blocks
    shown on the page. The ad blocks and additional data are used to
    compile a Page object.
    """
    all_ad_block_components: dict[AdBlockComponentType, list[AdBlockComponent]] = defaultdict(list)

    # Process each block annotation into an Ad Block Component
    for block_annotation in page_annotation.child_annotations:
        ad_block_components = extract_components_from_block(block_annotation)
        for ad_block_component in ad_block_components:
            all_ad_block_components[ad_block_component.component_type].append(ad_block_component)

    ad_blocks = construct_ad_blocks_from_components(all_ad_block_components)

    page = construct_page_from_ad_blocks(page_number, page_file_name, ad_blocks, page_annotation)

    return page


def process_flyer_annotation(page_annotations: list[HierarchicalAnnotation], flyer_name: str) -> Flyer:
    """
    Processes a list of page annotations into a Flyer object.
    """
    pages: list[Page] = []

    for page_number, page_annotation in enumerate(page_annotations):
        page = process_page_annotation(page_number, page_annotation)
        pages.append(page)

    flyer = construct_flyer_from_pages(pages, flyer_name)

    return flyer


def process_segmented_page_annotation(page_number: int, page_file_name: str, page_annotation: HierarchicalAnnotation, page_segmentation: list[Region]) -> Page:
    """
    Creates a list of ad blocks bounded by the page segmentation which
    contain the parsed data from the page annotations. These ad blocks
    are formed into a Page object.
    """
    ad_blocks: list[AdBlock] = []

    # Create an ad block for each segment
    for segment_bounds in page_segmentation:

        all_ad_block_components: defaultdict[AdBlockComponentType, list[AdBlockComponent]] = defaultdict(list)

        # Get all block annotations in the segmented block
        block_annotations = find_annotations_in_region(page_annotation.child_annotations, segment_bounds)

        for block_annotation in block_annotations:
            ad_block_components = extract_components_from_block(block_annotation)
            for ad_block_component in ad_block_components:
                all_ad_block_components[ad_block_component.component_type].append(ad_block_component)

        ad_block = construct_segmented_block_from_components(all_ad_block_components, segment_bounds)
        ad_blocks.append(ad_block)

    page = construct_page_from_ad_blocks(page_number, page_file_name, ad_blocks, page_annotation)
    return page


def process_segmented_flyer_annotations(
    page_file_names: list[str],
    page_annotations: list[HierarchicalAnnotation],
    page_segmentations: list[list[Region]],
    flyer_name: str
) -> Flyer:
    """
    Processes a list of pages and segmentation data into a Flyer object.
    """
    pages: list[Page] = []

    for page_number, (page_file_name, page_annotation, page_segmentation) in enumerate(zip(page_file_names, page_annotations, page_segmentations)):
        page = process_segmented_page_annotation(page_number, page_file_name, page_annotation, page_segmentation)
        pages.append(page)

    flyer = construct_flyer_from_pages(pages, flyer_name)
    return flyer


def construct_segmented_block_from_components(components: defaultdict[AdBlockComponentType, list[AdBlockComponent]], ad_block_bounds: Region) -> AdBlock:
    """
    Constructs an ad block that is bounded by the given ad_block_bounds
    and is created from the given set of components.

    Args:
        components (defaultdict[AdBlockComponentType, list[AdBlockComponent]]): Mapping from component type to all available components of that type
        ad_block_bounds (Region): Bounds of the ad block

    Returns:
        AdBlock: Constructed ad block
    """

    product_names = components[AdBlockComponentType.PRODUCT_NAME]
    product_descriptions = components[AdBlockComponentType.PRODUCT_DESCRIPTION]
    product_codes = components[AdBlockComponentType.PRODUCT_CODE]
    product_prices = components[AdBlockComponentType.PRODUCT_PRICE]
    product_price_units = components[AdBlockComponentType.PRODUCT_PRICE_UNIT]
    quantities = components[AdBlockComponentType.QUANTITY]
    promotions = components[AdBlockComponentType.PROMOTION]

    extra_components: list[AdBlockComponent] = []

    # TODO: Improve how to merge these components if find multiple!
    product_name = None
    if len(product_names) > 0:
        biggest_name_component, remaining_components = get_biggest_component(product_names)
        product_name = _get_component_value(biggest_name_component)

        # Convert the remaining product names to product descriptions
        product_descriptions.extend(remaining_components)

    description_values = [
        _get_component_value(description_component)
        for description_component in product_descriptions
        if _get_component_value(description_component) is not None
    ]

    product_description = None
    if len(description_values) > 0:
        # Normalize whitespace in the description
        product_description = ' '.join(' '.join(description_values).split())

    product_code = None
    if len(product_codes) > 0:
        product_code = _get_component_value(product_codes[0])
        extra_components.extend(product_codes[1:])

    product_price = None
    if len(product_prices) > 0:
        biggest_price_component, remaining_components = get_biggest_component(product_prices)
        product_price = _get_component_value(biggest_price_component)
        extra_components.extend(remaining_components)

    product_price_unit = None
    if len(product_price_units) > 0:
        product_price_unit = _get_component_value(product_price_units[0])
        extra_components.extend(product_price_units[1:])

    quantity = None
    if len(quantities) > 0:
        quantity = _get_component_value(quantities[0])
        extra_components.extend(quantities[1:])

    promotion = None
    if len(promotions) > 0:
        promotion = _get_component_value(promotions[0])
        extra_components.extend(promotions[1:])

    # Get the category from the product classifier
    product_category, confidence = None, None
    if product_name:
        product_category, confidence = product_classifier.classify(product_name)

    product = Product(
        name=product_name,
        description=product_description,
        code=product_code,
        category=CategoryPrediction(
            category=product_category,
            confidence=confidence
        ),
        price=product_price,
        price_unit=product_price_unit,
        quantity=quantity
    )

    additional_data = list(map(lambda component: str(component), extra_components))

    ad_block = AdBlock(product=product, promotion=promotion, bounds=ad_block_bounds, additional_data=additional_data)

    return ad_block


def construct_ad_blocks_from_components(components: defaultdict[AdBlockComponentType, list[AdBlockComponent]]) -> list[AdBlock]:
    """
    TODO: Update to use new AdBlockComponents and Product Classificaiton on product name

    Constructs ad blocks using the nearest components of each type.
    The number of ad blocks is equal to the number of price components.

    Args:
        components (defaultdict[AdBlockComponentType, list[AdBlockComponent]]): Available components of each type

    Returns:
        list[AdBlock]: The resulting ad blocks
    """
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


def get_nearest_component(from_component: AdBlockComponent, component_list: list[AdBlockComponent]) -> AdBlockComponent:
    """
    Gets the nearest component out of a list of components.

    Args:
        from_component (AdBlockComponent): The component to measure from
        component_list (list[AdBlockComponent]): Components to measure

    Returns:
        AdBlockComponent: The nearest component
    """
    nearest_component = None
    minimum_distance = float('inf')
    for to_component in component_list:
        distance_between_components = distance_between_regions(from_component.bounds, to_component.bounds)
        if distance_between_components < minimum_distance:
            nearest_component = to_component
            minimum_distance = distance_between_components

    return nearest_component


def get_component_group_bounds(components: list[AdBlockComponent]) -> Region:
    """
    Gets the minimum bounds that contains all of the components.
    """
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


def get_biggest_component(components: list[AdBlockComponent]) -> tuple[AdBlockComponent, list[AdBlockComponent]]:
    """
    Selects the component in the list with the largest bounds area.
    """
    biggest_component_idx = None
    biggest_component_size = 0
    for component_idx in range(len(components)):
        component = components[component_idx]
        if component is None or component.value is None:
            continue

        component_area = get_region_area(component.bounds)
        if component_area > biggest_component_size:
            biggest_component_size = component_area
            biggest_component_idx = component_idx

    if biggest_component_idx is None:
        return None, components

    biggest_component = components[biggest_component_idx]
    remaining_components = components[:biggest_component_idx] + components[biggest_component_idx+1:]

    return biggest_component, remaining_components


def contains_holiday_text(text: str) -> bool:
    """
    Returns whether or not the text contains a word from the holiday word list.
    """
    holiday_text_pattern = r'\b(' + '|'.join(HOLIDAY_WORD_LIST) + r')\b'
    holiday_match = re.search(holiday_text_pattern, text, flags=re.IGNORECASE)

    return holiday_match is not None


def _get_component_value(component: 'AdBlockComponent | None') -> Any:
    """
    Retrieves the value of the component, returning None if it is unable to.
    """
    if component is None:
        return None

    return component.value
