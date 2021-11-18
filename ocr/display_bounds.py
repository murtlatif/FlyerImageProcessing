from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
from util.constants import ANNOTATION_LEVEL_COLORS
from util.random_color import generate_random_color

from .annotation_types import (Annotation, AnnotationLevel,
                               HierarchicalAnnotation)


@dataclass
class AnnotationDrawData:
    lines: list[tuple[tuple[int, int]], tuple[int, int]]
    text_position: tuple[int, int]
    text: str
    annotation_level: AnnotationLevel


def draw_hierarchical_annotations(
    image_source: str,
    annotations: list[HierarchicalAnnotation],
    show_image: bool = True,
    annotation_level_whitelist: set[AnnotationLevel] = None
) -> Image.Image:
    """
    Draws a bounding box around each of the given hierarchical annotations and
    writes the text of the annotation inside the box.

    Used recursively by passing in the draw and image objects. If an image
    object is passed in, the image object will not be opened from the source.
    If a draw object is passed in, a new draw object will not be created.
    If show_image is True, the image will be displayed at the end.

    Args:
        image_source (str): Image to draw the annotations on
        annotations (list[HierarchicalAnnotation]): Hierarchical annotations
        show_image (bool): Whether to display the image at the end
        annotation_level_whitelist (set[AnnotationLevel]): The annotation levels to draw

    Returns:
        Image.Image: Resulting image with drawn annotations
    """

    image = Image.open(image_source)
    image = image_to_color(image)

    font = ImageFont.truetype('arial.ttf', 14)
    draw = ImageDraw.Draw(image)

    all_annotation_draw_data = _get_hierarchical_annotation_data_recursive(annotations)

    for annotation_draw_data in all_annotation_draw_data:
        # Skip annotations not in the whitelist
        if annotation_level_whitelist and annotation_draw_data.annotation_level not in annotation_level_whitelist:
            continue

        annotation_color = get_annotation_color(annotation_draw_data.annotation_level)

        # Draw the bounding box
        for line in annotation_draw_data.lines:
            draw.line(line, width=2, fill=annotation_color)

        # Draw the text
        draw.text(
            annotation_draw_data.text_position,
            text=annotation_draw_data.text,
            fill=annotation_color,
            font=font
        )

    if show_image:
        image.show()

    return image


def _get_hierarchical_annotation_data_recursive(annotations: list[HierarchicalAnnotation]) -> list[AnnotationDrawData]:
    """
    Recursively generates AnnotationDrawData containing the line and
    text information to be drawn from hierarchical annotations.

    Args:
        annotations (list[HierarchicalAnnotation]): The annotations to create draw data from

    Returns:
        list[AnnotationDrawData]: The drawing data
    """
    all_annotation_draw_data: list[AnnotationDrawData] = []

    for annotation in annotations:
        lines = []

        # Get all the lines connecting vertex[i] to vertex[i+1]
        for vertex_idx in range(len(annotation.bounds)):
            vertex_from = annotation.bounds[vertex_idx]
            vertex_to = annotation.bounds[(vertex_idx + 1) % len(annotation.bounds)]

            line = ((vertex_from.x, vertex_from.y), (vertex_to.x, vertex_to.y))
            lines.append(line)

        # Get the text data
        text_position = (annotation.bounds[0].x + 2, annotation.bounds[0].y)

        # Add current draw data
        annotation_draw_data = AnnotationDrawData(
            lines=lines,
            text_position=text_position,
            text=annotation.text,
            annotation_level=annotation.annotation_level
        )
        all_annotation_draw_data.append(annotation_draw_data)

        # Add child draw data recursively
        child_annotation_draw_data = _get_hierarchical_annotation_data_recursive(annotation.child_annotations)
        all_annotation_draw_data.extend(child_annotation_draw_data)

    return all_annotation_draw_data


def draw_flat_annotations(image_source: str, annotations: list[Annotation], show_image: bool = True) -> Image:
    """
    Draws a bounding box around each of the given annotations and writes the
    description of the annotation inside the box.

    Args:
        image_source (str): The image source to draw onto
        annotations (list[Annotation]): List of annotations
        show_image (bool): Whether to show the resulting image at the end

    Returns:
        Image: Resulting image with drawn annotations
    """
    image = Image.open(image_source)
    image = image_to_color(image)
    font = ImageFont.truetype('arial.ttf', 14)

    draw = ImageDraw.Draw(image)

    for annotation in annotations:

        annotation_color = generate_random_color()

        # Draw a line from vertex[i] to vertex[i+1]
        for vertex_idx in range(len(annotation.bounds)):
            vertex_from = annotation.bounds[vertex_idx]
            vertex_to = annotation.bounds[(vertex_idx + 1) % len(annotation.bounds)]

            line = ((vertex_from.x, vertex_from.y), (vertex_to.x, vertex_to.y))
            draw.line(line, width=2, fill=annotation_color)

        # Write the text
        text_position = (annotation.bounds[0].x + 2, annotation.bounds[0].y)
        draw.text(text_position, text=annotation.text, fill=annotation_color, font=font)

    if show_image:
        image.show()

    return image


def image_to_color(image: Image.Image) -> Image.Image:
    """
    Converts a 1 channel image to a 3 channel image. If an image that
    has more than 1 band is passed in, no conversion is performed.

    Args:
        image (Image.Image): The image to convert

    Returns:
        Image.Image: The colored image
    """
    is_grayscale = len(image.getbands()) == 1
    if is_grayscale:
        return Image.merge('RGB', [image, image, image])

    return image


def get_annotation_color(annotation_level: AnnotationLevel = None) -> tuple:
    """
    Gets a random color for a flat annotation (no annotation level),
    otherwise it gets the color from a map of annotation level to color.

    Args:
        annotation_level (AnnotationLevel, optional): Annotation level. Defaults to None.

    Returns:
        tuple: Resulting color
    """
    if annotation_level is None:
        return generate_random_color()

    return ANNOTATION_LEVEL_COLORS[annotation_level]
