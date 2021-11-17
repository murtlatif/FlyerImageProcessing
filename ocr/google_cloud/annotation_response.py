import os.path

from config import Config
from config.env_keys import OCR_OUTPUT_PATH
from google.cloud.vision import AnnotateImageResponse
from ocr.annotation_types import Annotation, HierarchicalAnnotation
from ocr.google_cloud.hierarchy_annotations import process_page_hierarchy
from util.file_path_util import apply_default_file_ext


def save_response_as_json(response: AnnotateImageResponse, file_name: str) -> str:
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


def load_response_as_flat_annotations(file_path: str) -> list[Annotation]:
    """
    Loads a text detection response JSON file into a list of Annotations.

    Args:
        file_path (str): File path to the response JSON file

    Returns:
        list[Annotation]: The flattened list of annotations
    """
    annotation_response = load_response_from_json(file_path)
    annotations = response_to_flat_annotations(annotation_response)

    return annotations


def load_response_as_hierarchical_annotations(file_path: str) -> list[HierarchicalAnnotation]:
    """
    Loads a text detection response JSON file into a list of
    HierarchicalAnnotations.

    Args:
        file_path (str): File path to the response JSON file

    Returns:
        list[HierarchicalAnnotations]: Annotations for the pages in the flyer
    """
    annotation_response = load_response_from_json(file_path)
    hierarchical_annotations = response_to_hierarchical_annotations(annotation_response)

    return hierarchical_annotations


def response_to_hierarchical_annotations(response: AnnotateImageResponse) -> list[HierarchicalAnnotation]:
    """
    Converts the response into a list of HierarchicalAnnotations.

    Args:
        response (AnnotateImageResponse): The response to convert from

    Returns:
        list[HierarchicalAnnotation]: Annotations of the pages in the response
    """
    page_annotations: list[HierarchicalAnnotation] = []

    for page in response.full_text_annotation.pages:
        page_annotation = process_page_hierarchy(page)
        page_annotations.append(page_annotation)

    return page_annotations


def response_to_flat_annotations(response: AnnotateImageResponse) -> list[Annotation]:
    """
    Converts the response into a list of Annotations.

    Args:
        response (AnnotateImageResponse): The response to convert from

    Returns:
        list[Annotation]: The list of flattened annotations
    """
    annotations: list[Annotation] = []

    for text_annotation in response.text_annotations:

        annotation = Annotation(
            bounds=text_annotation.bounding_poly.vertices,
            text=text_annotation.description
        )
        annotations.append(annotation)

    return annotations
