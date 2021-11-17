from PIL import Image, ImageDraw, ImageFont
from FlyerImageProcessing.ocr.annotation_types import AnnotationLevel, HierarchicalAnnotation
from FlyerImageProcessing.util.constants import ANNOTATION_LEVEL_COLORS, ANNOTATION_LEVEL_GRAYSCALE_COLORS
from util.random_color import generate_random_color

from ocr.annotation_types import Annotation


def draw_hierarchical_annotations(image_source: str, annotations: list[HierarchicalAnnotation]) -> Image:
    """
    Draws a bounding box around each of the given hierarchical annotations and
    writes the text of the annotation inside the box.

    Args:
        image_source (str): Image to draw the annotations on
        annotations (list[HierarchicalAnnotation]): Hierarchical annotations
    """
    image = Image.open(image_source)
    font = ImageFont.truetype('arial.ttf', 14)

    is_grayscale = len(image.getbands()) == 1

    draw = ImageDraw.Draw(image)

    for annotation in annotations:

        annotation_color = get_annotation_color(is_grayscale, annotation.annotation_level)

        # Draw a line from vertex[i] to vertex[i+1]
        for vertex_idx in range(len(annotation.bounds)):
            vertex_from = annotation.bounds[vertex_idx]
            vertex_to = annotation.bounds[(vertex_idx + 1) % len(annotation.bounds)]

            line = ((vertex_from.x, vertex_from.y), (vertex_to.x, vertex_to.y))
            draw.line(line, width=2, fill=annotation_color)

        # Write the text
        text_position = (annotation.bounds[0].x + 2, annotation.bounds[0].y)
        draw.text(text_position, text=annotation.text, fill=annotation_color, font=font)

    image.show()
    return image


def draw_flat_annotations(image_source: str, annotations: list[Annotation]) -> Image:
    """
    Draws a bounding box around each of the given annotations and writes the
    description of the annotation inside the box.

    Args:
        image_source (str): The image source to draw onto
        annotations (list[Annotation]): List of annotations
    """
    image = Image.open(image_source)
    font = ImageFont.truetype('arial.ttf', 14)

    image_channels = image.getbands()
    is_grayscale = len(image_channels) == 1

    draw = ImageDraw.Draw(image)

    for annotation in annotations:

        annotation_color = generate_random_color(is_grayscale)

        # Draw a line from vertex[i] to vertex[i+1]
        for vertex_idx in range(len(annotation.bounds)):
            vertex_from = annotation.bounds[vertex_idx]
            vertex_to = annotation.bounds[(vertex_idx + 1) % len(annotation.bounds)]

            line = ((vertex_from.x, vertex_from.y), (vertex_to.x, vertex_to.y))
            draw.line(line, width=2, fill=annotation_color)

        # Write the text
        text_position = (annotation.bounds[0].x + 2, annotation.bounds[0].y)
        draw.text(text_position, text=annotation.text, fill=annotation_color, font=font)

    image.show()
    return image


def get_annotation_color(grayscale: bool, annotation_level: AnnotationLevel = None) -> tuple:
    if annotation_level is None:
        return generate_random_color(grayscale)

    color_map = ANNOTATION_LEVEL_GRAYSCALE_COLORS if grayscale else ANNOTATION_LEVEL_COLORS
    return color_map[annotation_level]
