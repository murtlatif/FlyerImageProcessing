import re

from flyer.flyer_components import (AdBlock, AdBlockComponent,
                                    AdBlockComponentType, Measurement,
                                    Promotion, PromotionType, Quantity)

from .annotation_types import HierarchicalAnnotation


def ad_block_from_block_annotation(block_annotation: HierarchicalAnnotation) -> 'AdBlock | None':
    """
    Compiles an AdBlock object using the information found in the block
    annotation.

    Args:
        block_annotation (HierarchicalAnnotation): Block to compile

    Returns:
        AdBlock | None: Ad block if a price was found, otherwise None
    """
    # Identify the product price
    product_price = find_price_in_text(block_annotation.text)

    # TODO: Identify the product name
    product_name = block_annotation.text.split(' ')[0]

    # Identify the product quantity
    quantity = find_quantity_in_text(block_annotation.text)

    if product_price is None and quantity is None:
        return None

    ad_block = AdBlock(
        product_name=product_name,
        product_price=product_price,
        quantity=quantity,
        vertices=block_annotation.bounds
    )

    return ad_block


def extract_component_from_block(block_annotation: HierarchicalAnnotation) -> AdBlockComponent:
    # Check if the block is a quantity block
    quantity = find_quantity_in_text(block_annotation.text)
    if quantity is not None:
        return AdBlockComponent(
            AdBlockComponentType.QUANTITY,
            value=quantity,
            bounds=block_annotation.bounds
        )

    # Check if the block is a promotion
    promotion = find_promotion_in_text(block_annotation.text)
    if promotion is not None:
        return AdBlockComponent(
            AdBlockComponentType.PROMOTION,
            value=promotion,
            bounds=block_annotation.bounds
        )

    # Check if the block is a description
    if is_text_product_description(block_annotation.text):
        return AdBlockComponent(
            AdBlockComponentType.PRODUCT_DESCRIPTION,
            value=block_annotation.text,
            bounds=block_annotation.bounds
        )

    # Check if the block is a name
    if is_text_product_name(block_annotation.text):
        return AdBlockComponent(
            AdBlockComponentType.PRODUCT_NAME,
            value=block_annotation.text,
            bounds=block_annotation.bounds
        )

    # Check if the block is a price
    price = find_price_in_text(block_annotation.text)
    if price is not None:
        return AdBlockComponent(
            AdBlockComponentType.PRODUCT_PRICE,
            value=price,
            bounds=block_annotation.bounds
        )

    # Otherwise the component is unknown
    return AdBlockComponent(
        AdBlockComponentType.UNKNOWN,
        value=block_annotation,
        bounds=block_annotation.bounds
    )


def find_price_in_text(text: str) -> 'int | None':
    """
    Extracts the price in cents from the given text. If no price is found, None
    will be returned instead.

    Returns:
        int | None: Extracted price, or None if no price was found
    """
    price_regex_pattern = r'\$?(\d+(,\d+)*(\.\d+)?)\$?'
    price_regex_match = re.search(price_regex_pattern, text)
    if price_regex_match is None:
        return None

    # Strip commas and periods from the price
    price_string = price_regex_match.group(1)
    characters_to_strip_regex = r'[\.,]'
    stripped_price_string = re.sub(characters_to_strip_regex, '', price_string).strip()

    price = None
    try:
        price = int(stripped_price_string)
    except ValueError:
        print(f'Failed to convert price "{stripped_price_string}" to int.')

    return price


def find_quantity_in_text(text: str) -> 'Quantity | None':

    # Matches a measurement with an optional number in front (including decimals)
    measurements_union_regex = '(' + '|'.join(Measurement.valid_measurements()) + ')'
    quantity_regex_pattern = r'(((\d+(\.\d+)?)? +)|(\d+(\.\d+)?))' + measurements_union_regex + r'\b'

    quantity_regex_match = re.search(quantity_regex_pattern, text, flags=re.IGNORECASE)
    if quantity_regex_match is None:
        return None

    amount_string = quantity_regex_match.group(1)
    measurement_string = quantity_regex_match.group(7)

    # Process the amount
    stripped_amount_string = amount_string.strip()
    amount = None
    try:
        amount = float(stripped_amount_string)
    except ValueError:
        print(f'Failed to convert amount "{stripped_amount_string}" to float.')

    # Process the measurement
    measurement = None
    try:
        measurement = Measurement(measurement_string.lower())
    except ValueError:
        print(f'Failed to convert string "{measurement_string}" to Measurement.')

    quantity = Quantity(
        measurement=measurement,
        amount=amount
    )

    return quantity


def find_promotion_in_text(text: str) -> 'Promotion | None':
    PROMOTION_WORDS = ['sale', 'discount', 'up to', 'off', 'promotion', 'bogo', 'buy one get', 'free']
    amount_pattern = r'[$%]?\d+(\.\d+)?[$%]?'

    amount_match = re.search(amount_pattern, text)
    if amount_match is None:
        return None

    amount_string = amount_match.group(0)

    promotion_type = PromotionType.FLAT
    if '%' in amount_string:
        promotion_type = PromotionType.PERCENTAGE

    stripped_amount_string = amount_string.strip('$%.')

    amount = None
    try:
        amount = float(stripped_amount_string)
    except ValueError:
        print(f'Failed to convert amount "{stripped_amount_string}" to float.')
        return None

    # TODO: Implement other promotion types

    # Create the promotion component if the amount was a percentage
    if promotion_type == PromotionType.PERCENTAGE:
        promotion = Promotion(promotion_type=promotion_type, amount=amount, promotion_text=text)
        return promotion

    # Create the promotion component if the text contains promotion words
    for promotion_word in PROMOTION_WORDS:
        # Only consider a promotion if contains promotion word or
        if promotion_word in text.lower():
            promotion = Promotion(promotion_type=promotion_type, amount=amount, promotion_text=text)
            return promotion

    return None


def is_text_product_description(text: str) -> bool:
    has_many_words = len(text.split()) > 4
    has_alphabet = not text.isnumeric()

    if has_many_words and has_alphabet:
        return True


def is_text_product_name(text: str) -> bool:
    is_title_cased = (text.replace('\'', '').istitle() or text.isupper()) and not text.isnumeric()
    has_few_words = len(text.split()) < 4
    is_long_enough = len(text) > 3

    if is_title_cased and has_few_words and is_long_enough:
        return True

    return False
