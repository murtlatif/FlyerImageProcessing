from flyer.flyer_types import Page

from ocr.annotation_types import OCRAnnotation


def tokenize(text: str):
    return text.split()


def segment_page(page_annotations: list[OCRAnnotation]) -> Page:
    """
    Use OCRAnnotations from a page to create a Page object that the
    ad blocks shown on the page.

    Args:
        page_annotations (list[OCRAnnotation]): The OCRAnnotations found from the page

    Returns:
        Page: A page object containing the ad blocks on the page
    """
    price_annotations: list[OCRAnnotation] = []

    for annotation in page_annotations:
        annotation_token_list = tokenize(annotation.text)
        if '$' in annotation_token_list:
            price_annotations.append(annotation)
            continue

        print(f'Annotation tokens: {annotation}')
