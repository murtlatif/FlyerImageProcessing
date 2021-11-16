from google.cloud.vision import Page, Block, Paragraph, Word, Symbol
from ocr.annotation_types import OCRAnnotation


def process_page_hierarchy(page: Page) -> list[OCRAnnotation]:
    """
    Converts the response into a list of OCRAnnotations with the
    AnnotationType selected based on the hierarchy in the response.

    Args:
        response (AnnotateImageResponse): The response to convert from

    Returns:
        list[OCRAnnotation]: The list of OCRAnnotations
    """
    ocr_annotations: list[OCRAnnotation] = []

    for block in page.blocks:
        process_block_hierarchy(block)
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                word_text = []
                for symbol in word.symbols:
                    break_type = None
                    is_break_prefix = False
                    if symbol.hasattr('property') and symbol.property.hasattr('detected_break'):
                        break_type = symbol.property.detected_break.type_
                        is_break_prefix = symbol.property.detected_break.is_prefix

                    break_character = None
                    if break_type == 1:
                        break_character = ' '
                    elif break_type == 4:
                        break_character = '-'
                    elif break_type == 5:
                        break_character = '\n'

                    if is_break_prefix:
                        word_text.append(break_character)
                    word_text.append(symbol.text)


def process_block_hierarchy(block: Block) -> list[OCRAnnotation]:
    pass


def process_paragraph_hierarchy(paragraph: Paragraph) -> list[OCRAnnotation]:
    pass


def process_word_hierarchy(word: Word) -> list[OCRAnnotation]:
    pass


def process_symbol_hierarchy(symbol: Symbol) -> list[OCRAnnotation]:
    pass
