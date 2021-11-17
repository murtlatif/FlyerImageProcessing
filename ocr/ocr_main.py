import os.path

from config import Config
from flyer.flyer_types import Flyer
from flyer.marshal_flyer import marshal_flyer
from util.file_path_util import get_file_name_without_ext

from .annotation_types import Annotation
from .get_annotations import get_text_annotations
from .google_cloud.annotation_response import (
    load_response_from_json, response_to_flat_annotations,
    response_to_hierarchical_annotations)
from .ocr_segmentation import segment_page
from .display_bounds import draw_flat_annotations, draw_hierarchical_annotations, draw_text_annotations


def draw_annotations_on_image(
    image_path: str,
    annotation_json_path: str,
    hierarchical: bool = True,
    request_annotations: bool = False,
    save_file: str = None
):
    """
    Draws boxes around the annotations of an image. If `hierarchical` is True,
    the box color will be the same for all annotations of the same level.
    Otherwise, the box color will be randomized.

    Args:
        image_path (str): The image to draw boxes around
        annotation_json_path (str): The path to the annotations JSON
        hierarchical (bool, optional): Whether the annotations are hierarchical. Defaults to True.
        request_annotations (bool, optional): Whether to request for annotations if the annotation JSON is not valid. Defaults to False.
        save_file (str, optional): File name to save the annotations for if they were requested. Defaults to None.

    Returns:
        Image: The image with the annotation boundings drawn on
    """
    image_file_without_extension = get_file_name_without_ext(image_path)

    if annotation_json_path:
        response = load_response_from_json(annotation_json_path)
        if hierarchical:
            annotations = response_to_flat_annotations(response)
        else:
            annotations = response_to_hierarchical_annotations(response)

    else:
        annotations = get_text_annotations(file_image_path=image_path,
                                           request_as_fallback=request_annotations, save_file=save_file, hierarchical=hierarchical)

    if hierarchical:
        bounded_image = draw_hierarchical_annotations(image_path, annotations)
    else:
        bounded_image = draw_flat_annotations(image_path, annotations)

    bounded_image.save(f'bounded_{image_file_without_extension}.png')


def segment_with_ocr(hierarchical_annotations: list[Annotation]):
    segmented_page = segment_page(hierarchical_annotations)
    flyer = Flyer(
        pages=[
            segmented_page,
        ]
    )

    marshal_flyer(flyer, 'test_segmentation')
    return flyer


def ocr_main():
    image_path = Config.args.image_path

    hierarchical_annotations = get_text_annotations(
        annotation_json_path=Config.args.annotations_file,
        file_image_path=Config.args.image_path,
        request_as_fallback=Config.args.request_ocr,
        hierarchical=True
    )

    draw_hierarchical_annotations(image_path, hierarchical_annotations)
    # segment_with_ocr(page_annotations)
    # ocr_main(hierarchical_annotations)


if __name__ == '__main__':

    image_path = Config.args.image_path
    annotation_json_path = Config.args.annotations_file

    hierarchical_annotations = get_text_annotations(
        annotation_json_path=Config.args.annotations_file,
        file_image_path=Config.args.image_path,
        request_as_fallback=Config.args.request_ocr,
        hierarchical=True
    )

    draw_hierarchical_annotations(image_path, hierarchical_annotations)
    # segment_with_ocr(page_annotations)
    # ocr_main(hierarchical_annotations)
