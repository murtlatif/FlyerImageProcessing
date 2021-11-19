from google.cloud.vision_v1.types import Block, Page, Paragraph, Symbol, Word
from google.cloud.vision_v1.types.geometry import BoundingPoly
from ocr.annotation_types import AnnotationLevel, HierarchicalAnnotation
from util.image_space import Vertex, Region


def process_page_hierarchy(page: Page) -> HierarchicalAnnotation:
    """
    Processes a page as a HierarchicalAnnotation.

    Args:
        page (Page): Page to process

    Returns:
        HierarchicalAnnotation: Resulting annotation
    """
    block_annotations: list[HierarchicalAnnotation] = []
    page_text = ''

    for block in page.blocks:
        block_annotation = process_block_hierarchy(block)
        page_text += block_annotation.text
        block_annotations.append(block_annotation)

    # Pages don't have bounds, use (0, 0) and (width, height) as corners
    vertices = [
        Vertex(0, 0),
        Vertex(page.width, 0),
        Vertex(page.width, page.height),
        Vertex(0, page.height),
    ]
    page_annotation = HierarchicalAnnotation(bounds=vertices, text=page_text,
                                             annotation_level=AnnotationLevel.PAGE, child_annotations=block_annotations)

    return page_annotation


def process_block_hierarchy(block: Block) -> HierarchicalAnnotation:
    """
    Processes a block as a HierarchicalAnnotation.

    Args:
        block (Block): Block to process

    Returns:
        HierarchicalAnnotation: Resulting annotation
    """
    paragraph_annotations: list[HierarchicalAnnotation] = []
    block_text = ''

    for paragraph in block.paragraphs:
        paragraph_annotation = process_paragraph_hierarchy(paragraph)
        block_text += paragraph_annotation.text
        paragraph_annotations.append(paragraph_annotation)

    vertices = bounding_poly_to_vertex_list(block.bounding_box)
    block_annotation = HierarchicalAnnotation(bounds=vertices, text=block_text,
                                              annotation_level=AnnotationLevel.BLOCK, child_annotations=paragraph_annotations)

    return block_annotation


def process_paragraph_hierarchy(paragraph: Paragraph) -> HierarchicalAnnotation:
    """
    Processes a paragraph as a HierarchicalAnnotation.

    Args:
        paragraph (Paragraph): Paragraph to process

    Returns:
        HierarchicalAnnotation: Resulting annotation
    """
    word_annotations: list[HierarchicalAnnotation] = []
    paragraph_text = ''

    for word in paragraph.words:
        word_annotation = process_word_hierarchy(word)
        paragraph_text += word_annotation.text
        word_annotations.append(word_annotation)

    vertices = bounding_poly_to_vertex_list(paragraph.bounding_box)
    paragraph_annotation = HierarchicalAnnotation(bounds=vertices, text=paragraph_text,
                                                  annotation_level=AnnotationLevel.PARA, child_annotations=word_annotations)

    return paragraph_annotation


def process_word_hierarchy(word: Word) -> list[HierarchicalAnnotation]:
    """
    Processes a word as a HierarchicalAnnotation.

    Args:
        word (Word): Word to process

    Returns:
        HierarchicalAnnotation: Resulting annotation
    """
    symbol_annotations: list[HierarchicalAnnotation] = []
    word_text = ''

    for symbol in word.symbols:
        symbol_annotation = process_symbol_hierarchy(symbol)
        word_text += symbol_annotation.text
        symbol_annotations.append(symbol_annotation)

    vertices = bounding_poly_to_vertex_list(word.bounding_box)
    word_annotation = HierarchicalAnnotation(bounds=vertices, text=word_text,
                                             annotation_level=AnnotationLevel.WORD, child_annotations=symbol_annotations)

    return word_annotation


def process_symbol_hierarchy(symbol: Symbol) -> HierarchicalAnnotation:
    """
    Processes a symbol as a HierarchicalAnnotation.

    Args:
        symbol (Symbol): Symbol to process

    Returns:
        HierarchicalAnnotation: Resulting annotation
    """
    symbol_text = symbol.text
    detected_break = symbol.property.detected_break
    break_type = detected_break.type_
    is_break_prefix = detected_break.is_prefix

    break_character = ''

    if break_type == 4:
        break_character = '-'
    elif break_type == 5:
        break_character = '\n'
    elif break_type > 0:
        break_character = ' '

    if len(break_character) > 0:
        if is_break_prefix:
            symbol_text = break_character + symbol_text
        else:
            symbol_text = symbol_text + break_character

    vertices = bounding_poly_to_vertex_list(symbol.bounding_box)
    symbol_annotation = HierarchicalAnnotation(
        bounds=vertices, text=symbol_text, annotation_level=AnnotationLevel.SYMBOL)

    return symbol_annotation


def bounding_poly_to_vertex_list(bounding_poly: BoundingPoly) -> Region:
    """
    Converts a BoundingPoly object to a list of vertices

    Args:
        bounding_poly (BoundingPoly): The object to convert

    Returns:
        Region: The list of vertices
    """
    vertices = [Vertex.from_dict(vertex) for vertex in bounding_poly.vertices]
    return vertices
