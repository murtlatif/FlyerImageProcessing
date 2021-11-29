import os.path

from config import Config
from flyer.flyer_components import Flyer
from flyer.marshal_flyer import marshal_flyer
from Segmentation.GetBoxes import get_segmented_boxes
from util.constants import ANNOTATION_LEVEL_COLORS, COMMAND
from util.file_path_util import get_file_name_without_ext

from .annotation_types import AnnotationLevel, HierarchicalAnnotation
from .display_bounds import (draw_ad_blocks, draw_flat_annotations,
                             draw_hierarchical_annotations)
from .get_annotations import find_annotations_in_region, get_text_annotations
from .google_cloud.annotation_response import (
    load_response_from_json, response_to_flat_annotations,
    response_to_hierarchical_annotations)
from .process_annotations import (process_flyer_annotation,
                                  process_segmented_flyer_annotations)


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


def save_flyer(flyer: Flyer, file_path: str) -> None:
    marshal_flyer(flyer, file_path=file_path)


def draw_flyer_ad_blocks(flyer: Flyer, image_path: 'str | None') -> None:
    draw_ad_blocks(image_path, flyer.pages[0].ad_blocks)


def process_flyer(hierarchical_annotations: list[HierarchicalAnnotation]) -> Flyer:
    flyer = process_flyer_annotation(hierarchical_annotations)
    return flyer


def process_segmented_flyer(
    hierarchical_annotations: list[HierarchicalAnnotation],
    image_path: str,
    model_state_file: str,
) -> Flyer:
    image_file_name = os.path.basename(image_path)
    image_path_directory = os.path.dirname(image_path)
    segmented_boxes = get_segmented_boxes(image_file_name, model_state_file, image_path_directory)

    flyer = process_segmented_flyer_annotations(hierarchical_annotations, [segmented_boxes])
    return flyer


def ocr_main():
    image_path = Config.args.image_path
    model_state_file = Config.args.model_state
    annotation_file = Config.args.annotations_file

    hierarchical_annotations = get_text_annotations(
        annotation_json_path=Config.args.annotations_file,
        file_image_path=Config.args.image_path,
        request_as_fallback=Config.args.request_ocr,
        hierarchical=True
    )

    command = Config.args.command

    if command == COMMAND.ANNOTATIONS:
        if Config.args.verbose:
            print(hierarchical_annotations)

        if Config.args.display:
            draw_hierarchical_annotations(image_path, hierarchical_annotations, annotation_level_whitelist={
                AnnotationLevel.PAGE, AnnotationLevel.BLOCK})

    if command == COMMAND.FLYER:
        flyer = process_flyer(hierarchical_annotations)

        if Config.args.verbose:
            print(flyer)

        if Config.args.save:
            save_file_name = get_file_name_without_ext(annotation_file or image_path or 'UnnamedFlyer')
            save_flyer(flyer, file_path=save_file_name)

        if Config.args.display:
            draw_flyer_ad_blocks(flyer, image_path)

    if command == COMMAND.SEGMENTATION:
        flyer = process_segmented_flyer(hierarchical_annotations, image_path, model_state_file)

        if Config.args.verbose:
            print(flyer)

        if Config.args.save:
            save_file_name = get_file_name_without_ext(annotation_file or image_path or 'UnnamedFlyer')
            save_flyer(flyer, file_path=f'{save_file_name}_segmented')

        if Config.args.display:
            draw_flyer_ad_blocks(flyer, image_path)


if __name__ == '__main__':

    ocr_main()
