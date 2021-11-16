from PIL import Image, ImageDraw, ImageFont
from util.random_color import generate_random_color

from ocr.annotation_types import OCRAnnotation


def draw_text_annotations(image_source: str, annotations: list[OCRAnnotation]) -> None:
    """
    Draws a bounding box around each of the given annotations and writes the
    description of the annotation inside the box.

    Args:
        image_source (str): The image source to draw onto
        annotations (list[OCRAnnotation]): List of annotations
    """
    image = Image.open(image_source)
    font = ImageFont.truetype('arial.ttf', 14)

    draw = ImageDraw.Draw(image)
    for annotation in annotations:
        random_color = generate_random_color()
        bounds = annotation.bounds
        # Draw a line from vertex[i] to vertex[i+1]
        for vertex_idx in range(len(bounds)):
            vertex_from = bounds[vertex_idx]
            vertex_to = bounds[(vertex_idx + 1) % len(bounds)]

            line = ((vertex_from.x, vertex_from.y), (vertex_to.x, vertex_to.y))
            draw.line(line, width=2, fill=random_color)

        # Write the text
        text_position = (bounds[0].x + 2, bounds[0].y)
        draw.text(text_position, text=annotation.text, fill=random_color, font=font)

    image.show()
