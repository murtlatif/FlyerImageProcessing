from ocr.annotation_types import AnnotationLevel

ANNOTATION_LEVEL_COLORS = {
    AnnotationLevel.PAGE: (140, 20, 20),  # RED
    AnnotationLevel.BLOCK: (130, 20, 160),  # PINK
    AnnotationLevel.PARA: (110, 220, 180),  # LIGHT GREEN
    AnnotationLevel.WORD: (235, 210, 50),  # YELLOW
    AnnotationLevel.SYMBOL: (20, 20, 100),  # BLUE
}
