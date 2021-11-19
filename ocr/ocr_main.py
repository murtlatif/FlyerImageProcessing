from config import Config
from flyer.marshal_flyer import marshal_flyer
from util.constants import ANNOTATION_LEVEL_COLORS
from util.file_path_util import get_file_name_without_ext

from .annotation_types import AnnotationLevel
from .display_bounds import (draw_ad_blocks, draw_flat_annotations,
                             draw_hierarchical_annotations)
from .get_annotations import get_text_annotations
from .google_cloud.annotation_response import (
    load_response_from_json, response_to_flat_annotations,
    response_to_hierarchical_annotations)
from .process_annotations import process_flyer_annotation


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


def ocr_main():
    image_path = Config.args.image_path

    hierarchical_annotations = get_text_annotations(
        annotation_json_path=Config.args.annotations_file,
        file_image_path=Config.args.image_path,
        request_as_fallback=Config.args.request_ocr,
        hierarchical=True
    )

    # print(hierarchical_annotations)

    # draw_hierarchical_annotations(image_path, hierarchical_annotations, annotation_level_whitelist={
    #                               AnnotationLevel.PAGE, AnnotationLevel.BLOCK})

    flyer = process_flyer_annotation(hierarchical_annotations)
    file_name = get_file_name_without_ext(Config.args.image_path or Config.args.annotations_file or 'UnnamedFlyer')
    marshal_flyer(flyer, file_path=file_name)

    draw_ad_blocks(image_path, flyer.pages[0].ad_blocks)
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
