from ocr.annotation_types import AnnotationLevel

ANNOTATION_LEVEL_COLORS = {
    [AnnotationLevel.PAGE]: (140, 20, 20),  # RED
    [AnnotationLevel.BLOCK]: (130, 20, 160),  # PINK
    [AnnotationLevel.PARA]: (110, 220, 180),  # LIGHT GREEN
    [AnnotationLevel.WORD]: (235, 210, 50),  # YELLOW
    [AnnotationLevel.SYMBOL]: (20, 20, 100),  # BLUE
}

ANNOTATION_LEVEL_GRAYSCALE_COLORS = {
    [AnnotationLevel.PAGE]: (20,),  # DARKEST
    [AnnotationLevel.BLOCK]: (50,),
    [AnnotationLevel.PARA]: (80,),
    [AnnotationLevel.WORD]: (140,),
    [AnnotationLevel.SYMBOL]: (180,),  # LIGHTEST
}
