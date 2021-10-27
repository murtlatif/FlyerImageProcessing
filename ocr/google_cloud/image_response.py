import os.path

from config import Config
from config.env_keys import OCR_OUTPUT_PATH
from google.cloud.vision import AnnotateImageResponse
from ocr.ocr_annotation import OCRAnnotation


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
    file_path = file_name
    file_ext = os.path.splitext(file_path)[1]

    # Append .json file extension if no extension given
    if file_ext == '':
        file_path += '.json'

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
