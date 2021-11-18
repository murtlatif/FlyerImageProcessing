from flyer.flyer_types import Page

from .annotation_types import Annotation, HierarchicalAnnotation


def tokenize(text: str):
    return text.split()


def segment_page(page_annotations: list[HierarchicalAnnotation]) -> Page:
    """
    Use Annotations from a page to create a Page object that contains the ad
    blocks shown on the page.

    Args:
        page_annotations (list[Annotation]): The Annotation found from the page

    Returns:
        Page: A page object containing the ad blocks on the page
    """
    price_annotations: list[Annotation] = []

    for page_annotation in page_annotations:
        annotation_token_list = tokenize(page_annotation.text)
        if '$' in annotation_token_list:
            price_annotations.append(page_annotation)
            continue

        print(f'Annotation tokens: {page_annotation}')
