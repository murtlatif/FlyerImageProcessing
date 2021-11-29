import os
import os.path

from config import Config
from ocr.annotation_types import HierarchicalAnnotation
from ocr.get_annotations import get_text_annotations
from ocr.ocr_main import draw_flyer_ad_blocks, save_flyer
from ocr.process_annotations import process_segmented_flyer_annotations
from pipeline.convert_pdf import convert_pdf_to_image
from pipeline.flyer_preprocess import PreprocessType, preprocess_image_file
from Segmentation.GetBoxes import get_segmented_boxes
from util.constants import VALID_IMAGE_FILE_TYPES
from util.file_path_util import (apply_default_file_ext,
                                 get_file_name_without_ext, has_extension)
from util.image_space import Region

"""
If you haven't yet, run the program with the `--download` flag to download
the NLTK packages for grammar parsing.

Sample command to run the program:

```
python main.py -r -v -sm Segmentation/models/my_model -cm classificaton/model/path --save
```
"""


def get_preprocessed_image(image_path: str, preprocess_folder_name: str, preprocess_type: PreprocessType = PreprocessType.BILATERAL) -> str:
    """
    Takes in a directory or file path and preprocesses the given image, or all
    of the images in the directory.

    Returns the new path to the preprocessed file/directory.
    """
    input_path_directory, input_file_name = os.path.split(image_path)
    input_file_name = f'{preprocess_type.value}_{input_file_name}'
    preprocessed_file_path = os.path.join(input_path_directory, preprocess_folder_name, input_file_name)

    if not os.path.exists(preprocessed_file_path):
        preprocess_image_file(image_path, output_path=preprocessed_file_path, preprocess_type=PreprocessType.BILATERAL)

    return preprocessed_file_path


def get_annotation_file_path(input_file_path: str, annotation_folder_name: str) -> 'str':
    """
    Takes in an image file path and outputs the file path of the corresponding
    annotation.
    """
    input_path_directory, input_file_name = os.path.split(input_file_path)
    annotation_file_name = apply_default_file_ext(input_file_name, '.json', force=True)
    annotation_file_path = os.path.join(input_path_directory, annotation_folder_name, annotation_file_name)

    return annotation_file_path


def perform_ocr_on_file(input_file: str, annotation_folder_name: str, preprocess: bool = True, preprocess_folder_name: str = None):
    """
    Retrieves annotations of an input image. Will make requests if annotation
    is not found and the request_ocr flag is enabled.

    Returns a tuple of the input file name and the annotations
    """
    annotation_file_path = get_annotation_file_path(input_file, annotation_folder_name)

    annotation_image_path = input_file
    if preprocess:
        preprocessed_image_file_path = get_preprocessed_image(input_file, preprocess_folder_name)
        annotation_image_path = preprocessed_image_file_path

    annotations = get_text_annotations(
        annotation_json_path=annotation_file_path,
        file_image_path=annotation_image_path,
        request_as_fallback=Config.args.request_ocr,
        save_file_path=annotation_file_path,
        hierarchical=True,
        use_default_directory=False,
    )

    return annotations


def perform_ocr(input_path: str, annotation_folder_name: str, preprocess: bool = True, preprocess_folder_name: str = None):
    """
    Takes in a directory or file path and gets the corresponding annotations,
    requesting OCR from the Google Cloud Client if the annotations were not
    found in the directory. Will preprocess the images if preprocess is True.
    Valid input image files are `.pdf`, `.png`, `.jpg`, `.jpeg`

    Raises a ValueError if preprocess is True and preprocess_folder_name is None.
    Returns a list of tuples, where each tuple is the input_file_path and the list of annotations.
    """
    annotation_outputs: list[tuple[str, list[HierarchicalAnnotation]]] = []
    files_to_process: list[str] = []

    if preprocess and preprocess_folder_name is None:
        raise ValueError('preprocess_folder_name must be provided if preprocess is set to True!')

    if not os.path.exists(input_path):
        return annotation_outputs

    if os.path.isfile(input_path):
        if has_extension(input_path, {'.pdf'}):
            pdf_image_paths = convert_pdf_to_image(input_path)
            files_to_process.extend(pdf_image_paths)

        if has_extension(input_path, VALID_IMAGE_FILE_TYPES):
            files_to_process.append(input_path)

    # If input path is directory
    for entry in os.scandir(input_path):
        if not entry.is_file():
            continue

        if has_extension(entry.name, valid_extensions={'.pdf'}):
            pdf_image_paths = convert_pdf_to_image(input_path)
            files_to_process.extend(pdf_image_paths)

        if has_extension(entry.name, valid_extensions=VALID_IMAGE_FILE_TYPES):
            files_to_process.append(entry.path)

    # Process all files
    for file_idx, file_to_process in enumerate(files_to_process):
        if Config.args.verbose:
            print(
                f'[PROCESSING] {file_idx + 1}/{len(files_to_process)} ({(file_idx+1)/len(files_to_process):.2%}): {file_to_process}'
            )
        annotations = perform_ocr_on_file(file_to_process, annotation_folder_name, preprocess, preprocess_folder_name)
        annotation_outputs.append((file_to_process, annotations))

    return annotation_outputs


def process_segmented_flyer(image_path: str, annotations: list[HierarchicalAnnotation], segmentation_map: dict[str, list[Region]]):
    """
    Uses the segmentation bounds given by the segmentation_map and image_path
    to process a Flyer object from the annotations.
    """
    image_file_name = os.path.basename(image_path)
    segmentations = [segmentation_map[image_file_name]]

    flyer = process_segmented_flyer_annotations(annotations, segmentations)
    return flyer


if __name__ == '__main__':

    # Initialization
    ANNOTATION_DATA_FOLDER = Config.env.DATA_ANNOTATION_PATH or 'ocr_annotations'
    OUTPUT_FLYER_FOLDER = Config.env.DATA_FLYER_OUTPUT_PATH or 'out'
    PREPROCESSED_DATA_FOLDER = Config.env.DATA_PREPROCESSED_PATH or 'preprocessed'

    input_path = Config.env.INPUT_PATH
    input_path_directory = input_path if os.path.isdir(input_path) else os.path.dirname(input_path)

    if not os.path.exists(input_path):
        raise ValueError(f'Input path "{input_path}" does not exist!')

    annotation_data = perform_ocr(input_path, ANNOTATION_DATA_FOLDER, preprocess=True,
                                  preprocess_folder_name=PREPROCESSED_DATA_FOLDER)

    segmentation_bounds = get_segmented_boxes(Config.args.segmentation_model_state, input_path_directory)

    for idx, (image_path, annotations) in enumerate(annotation_data):
        flyer = process_segmented_flyer(image_path, annotations, segmentation_bounds)

        if Config.args.verbose:
            print(
                f'[SEGMENTATION] {idx+1}/{len(annotation_data)} ({(idx+1)/len(annotation_data):.2%}): {image_path}')

        if Config.args.verbose > 1:
            print(flyer)

        if Config.args.save:
            output_file_name = get_file_name_without_ext(image_path)
            output_file_path = os.path.join(input_path_directory, OUTPUT_FLYER_FOLDER, output_file_name)
            save_flyer(flyer, file_path=output_file_path)

        if Config.args.display:
            draw_flyer_ad_blocks(flyer, image_path)
