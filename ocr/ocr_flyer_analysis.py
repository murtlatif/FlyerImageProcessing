import re

from config import Config
from flyer.flyer_components import (AdBlockComponent, AdBlockComponentType,
                                    Promotion, PromotionType, Quantity)
from util.constants import (MEASUREMENT_WORD_LIST, PACKAGE_MEASURE_WORD_LIST,
                            PROMOTION_WORDS)
from util.string_parse import (string_to_any_safe, string_to_float_safe,
                               string_to_int_safe)

from ocr.grammar_parser import Grammar, PhraseExtractor

from .annotation_types import HierarchicalAnnotation


def extract_components_from_block(block_annotation: HierarchicalAnnotation) -> list[AdBlockComponent]:
    """
    Extracts all of the ad block components from a given block.

    TODO: Improve analysis further by adding additional rules or
    features.
    """
    components: AdBlockComponent = []
    component_types_found: set[AdBlockComponentType] = set()

    component_extractors = [
        (AdBlockComponentType.PRODUCT_NAME, extract_product_name_component),
        (AdBlockComponentType.PRODUCT_CODE, extract_product_code_component),
        (AdBlockComponentType.PRODUCT_PRICE, extract_price_component),
        (AdBlockComponentType.PRODUCT_PRICE_UNIT, extract_price_unit_component),
        (AdBlockComponentType.QUANTITY, extract_quantity_component),
        (AdBlockComponentType.PROMOTION, extract_promotion_component),
        (AdBlockComponentType.PRODUCT_DESCRIPTION, extract_product_description_component),
    ]

    for component_type, component_extractor in component_extractors:

        if (component_type == AdBlockComponentType.PRODUCT_DESCRIPTION and (
            AdBlockComponentType.PRODUCT_NAME in component_types_found or
            AdBlockComponentType.PROMOTION in component_types_found
        )):
            continue

        component = component_extractor(block_annotation)
        if component is not None:
            components.append(component)

    if not components:
        # Check if product description if no other components found
        product_description_component = extract_product_description_component(block_annotation)
        if product_description_component:
            components.append(product_description_component)
        else:
            # Otherwise the component is unknown
            components.append(AdBlockComponent(
                AdBlockComponentType.UNKNOWN,
                value=block_annotation,
                bounds=block_annotation.bounds
            ))

    return components


def extract_product_code_component(block: HierarchicalAnnotation) -> 'AdBlockComponent | None':
    """
    Extracts the product code from the text. The product code is set in the
    environment configuration.
    """
    text = ' '.join(block.text.split())

    product_code_regex = Config.env.PRODUCT_CODE_REGEX
    multi_product_code_regex = product_code_regex + r'([-\/ ]' + product_code_regex + r')?'
    product_code_match = re.search(multi_product_code_regex, text)

    if product_code_match is None:
        return None

    product_code = product_code_match.group()

    product_code_component = AdBlockComponent(
        AdBlockComponentType.PRODUCT_CODE,
        value=product_code,
        bounds=block.bounds
    )

    return product_code_component


def extract_quantity_component(block: HierarchicalAnnotation) -> 'AdBlockComponent | None':
    """
    Extracts the quantity/measurement of the block (e.g. "4 lb" or "2.1kg")
    """
    text = ' '.join(block.text.split())

    # Check if the measurement is "PKG OF N"
    package_unit_pattern = '|'.join(PACKAGE_MEASURE_WORD_LIST)
    pkg_of_pattern = '((' + package_unit_pattern + r') of )(((\d+(\.\d+)?) ?[-\/x] ?)?(\d+(\.\d+)?))'
    pkg_of_match = re.search(pkg_of_pattern, text, flags=re.IGNORECASE)

    if pkg_of_match:
        quantity_unit = pkg_of_match.group(1)
        quantity_amount = pkg_of_match.group(3)

        quantity = Quantity(
            measurement=quantity_unit.strip(),
            amount=quantity_amount,
            text=text
        )

        quantity_component = AdBlockComponent(
            AdBlockComponentType.QUANTITY,
            value=quantity,
            bounds=block.bounds,
        )

        return quantity_component

    # Matches a measurement with an optional number in front (including decimals)
    measurements_union_regex = '(' + '|'.join(MEASUREMENT_WORD_LIST) + ')'
    quantity_amount_regex = r'(((\d+(\.\d+)?) ?[-\/x] ?)?(\d+(\.\d+)?) ?)'
    quantity_regex_pattern = quantity_amount_regex + measurements_union_regex + r'\b'

    quantity_regex_match = re.search(quantity_regex_pattern, text, flags=re.IGNORECASE)
    if quantity_regex_match is None:
        return None

    full_amount_string = quantity_regex_match.group(1).strip()
    amount_prefix_string = quantity_regex_match.group(2)
    amount_string = quantity_regex_match.group(5)
    measurement = quantity_regex_match.group(7).strip()

    # Process the amount and measurement
    stripped_amount_string = amount_string.strip()
    amount = string_to_float_safe(stripped_amount_string)

    if amount_prefix_string is None and (amount is None or amount >= 10000):
        return None

    quantity = Quantity(
        measurement=measurement,
        amount=full_amount_string.strip(),
        text=text,
    )

    quantity_component = AdBlockComponent(
        AdBlockComponentType.QUANTITY,
        value=quantity,
        bounds=block.bounds,
    )

    return quantity_component


def extract_price_component(block: HierarchicalAnnotation) -> 'AdBlockComponent | None':
    """
    Extracts the price in cents from the given text. If no price is found, None
    will be returned instead.
    """
    text = ' '.join(block.text.lower().split())

    # Is price a X/$Y format? (e.g. 2/$3 or 3 for $4)
    x_for_y_regex_pattern = r'(\d+) ?(\/|for) ?([\$s] ?)?(\d+(\.\d+)?)'
    x_for_y_match = re.match(x_for_y_regex_pattern, text)

    if x_for_y_match:
        quantity_string = x_for_y_match.group(1)
        price_string = x_for_y_match.group(4)

        quantity = string_to_int_safe(quantity_string)
        price = _string_to_price(price_string)

        if quantity and quantity < 10 and price:
            price_component = AdBlockComponent(
                AdBlockComponentType.PRODUCT_PRICE,
                value=price/quantity,
                bounds=block.bounds,
            )

            return price_component

    # Is the price in a $/<MEASUREMENT> format?
    price_per_pattern = r'\$?(\d+(\.\d+)?) ?\/ ?\w+'
    price_per_match = re.match(price_per_pattern, text)
    if price_per_match:
        price_string = price_per_match.group(1)
        price = _string_to_price(price_string)

        if price:
            price_component = AdBlockComponent(
                AdBlockComponentType.PRODUCT_PRICE,
                value=price,
                bounds=block.bounds,
            )

            return price_component

    # Finally: Price is just a number on its own
    price_regex_pattern = r'\$?(\d+(\.\d+)?)?'
    price_regex_match = re.search(price_regex_pattern, text)
    if price_regex_match is None:
        return None

    price_string = price_regex_match.group(1)
    price = _string_to_price(price_string)

    if price is None:
        return None

    price_component = AdBlockComponent(
        AdBlockComponentType.PRODUCT_PRICE,
        value=price,
        bounds=block.bounds,
    )

    return price_component


def extract_promotion_component(block: HierarchicalAnnotation) -> 'AdBlockComponent | None':
    """
    Extracts the promotion component from a block. Promotions are
    determined by a percentage value or by promotional keywords.
    """
    text = ' '.join(block.text.split())

    # Check if has BOGO or BNGO (Buy N Get One) promotion
    bogo_pattern = r'(buy (\d|one) (and ?)?get (1|one)( free)?)|\bbogo\b'
    bogo_match = re.search(bogo_pattern, text, flags=re.IGNORECASE)
    if bogo_match:
        amount_string = bogo_match.group(2)
        amount = string_to_int_safe(amount_string)

        n_value = 1
        if amount and amount > 0 and amount < 10:
            n_value = amount

        promotion = Promotion(
            PromotionType.BUY_N_GET_ONE_FREE,
            amount=str(n_value),
            promotion_text=text,
        )

        promotion_component = AdBlockComponent(
            AdBlockComponentType.PROMOTION,
            value=promotion,
            bounds=block.bounds,
        )

        return promotion_component

    # TODO: Check other promotion types here

    # Finally: Check for amount value and generic promotion text
    # (\$?(\d+(\.\d+)?)%? ?- ?)?(\$?(\d+(\.\d+)?)%?)
    amount_pattern = r'(\$?(\d+(\.\d+)?)%? ?- ?)?(\$?(\d+(\.\d+)?)%?)'
    amount_match = re.search(amount_pattern, text)
    if amount_match is None:
        return None

    full_amount_string = amount_match.group()

    # Get amount and promotion type for percentage vs dollars
    if '%' in full_amount_string:
        promotion_type = PromotionType.PERCENTAGE
    else:
        promotion_type = PromotionType.FLAT

    # Only consider to be promotion if have value AND promotion text
    promotion = None
    for promotion_word in PROMOTION_WORDS:
        if promotion_word in text.lower():
            promotion = Promotion(
                promotion_type=promotion_type,
                amount=full_amount_string,
                promotion_text=text,
            )
            break

    if promotion is None:
        return None

    promotion_component = AdBlockComponent(
        AdBlockComponentType.PROMOTION,
        value=promotion,
        bounds=block.bounds,
    )

    return promotion_component


def extract_price_unit_component(block: HierarchicalAnnotation) -> 'AdBlockComponent | None':
    """
    Extract the unit of the price from a block.
    """
    text = ' '.join(block.text.lower().split())

    price_unit = None

    # Check if the text is directly common price unit terms
    if text in {'ea', 'each'}:
        price_unit = 'each'

        price_unit_component = AdBlockComponent(
            AdBlockComponentType.PRODUCT_PRICE_UNIT,
            value=price_unit,
            bounds=block.bounds,
        )

        return price_unit_component

    # Extract price unit as EACH for a X/$Y format (e.g. 2/$3 or 3 for $4)
    x_for_y_regex_pattern = r'(\d+) ?(\/|for) ?([\$s] ?)?(\d+(\.\d+)?)'
    x_for_y_match = re.match(x_for_y_regex_pattern, text)

    if x_for_y_match:
        price_unit = 'each'
        price_unit_component = AdBlockComponent(
            AdBlockComponentType.PRODUCT_PRICE_UNIT,
            value=price_unit,
            bounds=block.bounds,
        )

        return price_unit_component

    # Extract price unit as MEASUREMENT from $/<MEASUREMENT> format
    price_per_pattern = r'\$?(\d+(\.\d+)?) ?\/ ?(\w+)'
    price_per_match = re.match(price_per_pattern, text)
    if price_per_match:
        price_unit = price_per_match.group(3)
        price_unit_component = AdBlockComponent(
            AdBlockComponentType.PRODUCT_PRICE_UNIT,
            value=price_unit,
            bounds=block.bounds,
        )

        return price_unit_component

    # Find a measurement without a value
    measurements_union_regex = '(' + '|'.join(MEASUREMENT_WORD_LIST) + ')'
    optional_number_regex = r'(((\d+(\.\d+)?) ?)|\b)'
    quantity_regex_pattern = optional_number_regex + measurements_union_regex + r'\b'

    quantity_regex_match = re.search(quantity_regex_pattern, text, flags=re.IGNORECASE)
    if quantity_regex_match is None:
        return None

    amount_string = quantity_regex_match.group(1)
    measurement_string = quantity_regex_match.group(5)

    if amount_string:
        return None

    price_unit = measurement_string
    price_unit_component = AdBlockComponent(
        AdBlockComponentType.PRODUCT_PRICE_UNIT,
        value=price_unit,
        bounds=block.bounds,
    )

    return price_unit_component


def extract_product_name_component(block: HierarchicalAnnotation) -> 'AdBlockComponent | None':
    """
    Extracts the product name by using noun phrases.
    """
    text = block.text

    # Filter out company-specific product names
    ignore_in_product_name_string = Config.env.IGNORE_IN_PRODUCT_NAME
    ignore_patterns = []
    if ignore_in_product_name_string:
        ignore_patterns = ignore_in_product_name_string.split(';')

    for ignore_pattern in ignore_patterns:
        text = re.sub(ignore_pattern, '', text, flags=re.IGNORECASE)

    # Renormalize the text
    text = ' '.join(text.split())

    # Filter out 'product of X (or Y)'
    proper_nouns = PhraseExtractor.extract_phrases(text, Grammar.PROPER_NOUN_PHRASE)
    filtered_proper_nouns = [proper_noun for proper_noun in proper_nouns if len(proper_noun) > 2]

    for proper_noun in filtered_proper_nouns:
        proper_noun = proper_noun.replace('U S A', 'U.S.A.')
        product_of_phrase = 'product of ' + proper_noun
        text = text.replace(product_of_phrase, '')

    # Renormalize text again
    text = ' '.join(text.split())

    # Avoid taking words like "LB" for a product name
    if len(text) < 5:
        return None

    extracted_noun_phrases = PhraseExtractor.extract_phrases(text, Grammar.NOUN_PHRASE)
    filtered_noun_phrases = [noun_phrase for noun_phrase in extracted_noun_phrases if len(noun_phrase) > 5]

    product_name = None
    if len(filtered_noun_phrases) > 0:
        product_name = filtered_noun_phrases[0]

    if product_name is None:
        return None

    product_name_component = AdBlockComponent(
        AdBlockComponentType.PRODUCT_NAME,
        value=product_name,
        bounds=block.bounds,
    )

    return product_name_component


def extract_product_description_component(block: HierarchicalAnnotation) -> 'AdBlockComponent | None':
    """
    Extracts the product description using basic rules.
    """
    text = ' '.join(block.text.split())
    if text.isnumeric():
        return None

    num_words = len(text.split())
    if num_words < 5:
        return None

    product_description_component = AdBlockComponent(
        AdBlockComponentType.PRODUCT_DESCRIPTION,
        value=text,
        bounds=block.bounds
    )

    return product_description_component


def _string_to_price(text: str) -> 'int | None':
    """
    Convert a string to a price value in cents
    """
    if text is None:
        return None

    characters_to_strip_regex = r'[\.,]'
    stripped_price_string = re.sub(characters_to_strip_regex, '', text)
    price = string_to_float_safe(stripped_price_string)

    if price is None:
        return None

    # Convert to cents if price is dollar value or has decimals
    if price < 20 or price % 1 != 0:
        price *= 100

    # Valid prices range from $0.20 to $100
    if price < 20 or price > 10000:
        return None

    return int(price)
