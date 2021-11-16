import os.path

from config import Config
from config.env_keys import OCR_OUTPUT_PATH
from google.cloud.vision import AnnotateImageResponse
from ocr.annotation_types import OCRAnnotation
from util.file_path_util import apply_default_file_ext


def save_response_as_json(response: AnnotateImageResponse, file_name: str):
    """
    Saves a text detection response object as a JSON file.

    Args:
        response (AnnotateImageResponse): The response from the Cloud Vision text detection
        file_name (str): The file name to save the JSON as

    Returns:
        str: The response object represented as a JSON string
    """
    response_json = AnnotateImageResponse.to_json(response)
    file_path = apply_default_file_ext(file_name, '.json')

    # Prepend OCR_OUTPUT_PATH if the value is set
    if OCR_OUTPUT_PATH in Config.env:
        file_path = os.path.join(Config.env.OCR_OUTPUT_PATH, file_path)

    with open(file_path, 'w') as response_json_file:
        response_json_file.write(response_json)

    return response_json


def load_response_from_json(file_path: str) -> AnnotateImageResponse:
    """
    Loads a text detection response JSON file into an AnnotateImageResponse
    object.

    Args:
        file_path (str): The file path to the response JSON file

    Returns:
        AnnotateImageResponse: The response object.
    """
    with open(file_path, 'r') as response_json_file:
        response_json = response_json_file.read()
        response = AnnotateImageResponse.from_json(response_json)

    return response


def load_response_as_ocr_annotation(file_path: str):
    """
    Loads a text detection response JSON file into a list of
    OCRAnnotations.

    Args:
        file_path (str): The file path to the response JSON file
    """
    annotation_response = load_response_from_json(file_path)
    ocr_annotations = response_to_ocr_annotations(annotation_response)

    return ocr_annotations


def response_to_hierarchy_annotation(response: AnnotateImageResponse):
    """
    Converts the response into a list of OCRAnnotations with the
    AnnotationType selected based on the hierarchy in the response.

    Args:
        response (AnnotateImageResponse): The response to convert from

    Returns:
        list[OCRAnnotation]: The list of OCRAnnotations
    """
    ocr_annotations: list[OCRAnnotation] = []

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = []
                    for symbol in word.symbols:
                        break_type = None
                        is_break_prefix = False
                        if symbol.hasattr('property') and symbol.property.hasattr('detected_break'):
                            break_type = symbol.property.detected_break.type_
                            is_break_prefix = symbol.property.detected_break.is_prefix

                        break_character = None
                        if break_type == 1:
                            break_character = ' '
                        elif break_type == 4:
                            break_character = '-'
                        elif break_type == 5:
                            break_character = '\n'

                        if is_break_prefix:
                            word_text.append(break_character)
                        word_text.append(symbol.text)


def response_to_ocr_annotations(response: AnnotateImageResponse):
    """
    Converts the response into a list of OCRAnnotations.

    Args:
        response (AnnotateImageResponse): The response to convert from

    Returns:
        list[OCRAnnotation]: The list of OCRAnnotations
    """
    ocr_annotations: list[OCRAnnotation] = []

    for text_annotation in response.text_annotations:

        annotation = OCRAnnotation(
            bounds=text_annotation.bounding_poly.vertices,
            text=text_annotation.description
        )
        ocr_annotations.append(annotation)

    return ocr_annotations
