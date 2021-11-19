from util.file_path_util import get_file_name_without_ext
from util.image_space import Vertex, does_region_intersect

from .annotation_types import Annotation
from .google_cloud import google_cloud_client
from .google_cloud.annotation_response import (
    load_response_from_json, response_to_flat_annotations,
    response_to_hierarchical_annotations, save_response_as_json)


def get_text_annotations(
    annotation_json_path: str,
    file_image_path: str,
    request_as_fallback: bool = False,
    save_file: str = None,
    hierarchical: bool = True
) -> list[Annotation]:
    """
    Gets OCR annotation from the annotation JSON file given, or requests
    annotations for the image specified if request_as_fallback is True.

    Requests annotation from the image if an image path is provided. If an
    annotation is requested, the annotation data will be saved to the path
    specified by save_file. If no save_file is given, the file name will be set
    to the file_image_path value.

    Args:
        annotation_json_path (str): The annotation data file to load
        file_image_path (str): The path to the image to annotate
        rqeuest_as_fallback (bool, optional): Whether to request annotations if failed to load from JSON. Defaults to False.
        save_file (str, optional): The name to save the annotated file as if an annotation was requested. Defaults to the image file name.
        hierarchical (bool, optional): Whether to load the annotations using the hierarchical model. If False, will load flat annotations. Defaults to True.

    Raises:
        ValueError: If no path is given for the annotation JSON or the image

    Returns:
        list[Annotation]: The list of annotations
    """
    if annotation_json_path:
        response = load_response_from_json(annotation_json_path)

        if hierarchical:
            annotations = response_to_hierarchical_annotations(response)
        else:
            annotations = response_to_flat_annotations(response)

    elif request_as_fallback and file_image_path is not None:
        annotations = request_text_annotations(file_image_path, save_file=save_file, hierarchical=hierarchical)

    else:
        raise ValueError(f'No path given for annotation JSON or image.')

    return annotations


def request_text_annotations(file_image_path: str, save_file: str = None, hierarchical: bool = True) -> list[Annotation]:
    """
    Requests text annotations from Google Cloud and saves the data as a JSON
    file. If no save_file_name is given, the file_image_path is used instead.

    Args:
        file_image_path (str): The path to the image to annotate
        save_file (str, optional): The file name to save the annotation data as. Defaults to the image file name.
        hierarchical (bool, optional): Whether to get the hierarchical annotations. Will get flat annotations if False. Defaults to True.

    Returns:
        list[Annotation]: The list of annotations
    """
    annotation_response = google_cloud_client.request_text_detection(file_image_path)

    if save_file is None:
        save_file = file_image_path

    save_file = get_file_name_without_ext(save_file)
    save_response_as_json(annotation_response, save_file)

    if hierarchical:
        annotations = response_to_hierarchical_annotations(annotation_response)
    else:
        annotations = response_to_flat_annotations(annotation_response)

    return annotations


def find_annotations_in_region(
    annotations: list[Annotation],
    region_vertices: list[Vertex],
) -> list[Annotation]:
    """
    Filters the list of annotations to all of the annotations that
    intersect the specified region.

    Args:
        annotations (list[Annotation]): Annotations to filter
        region_vertices (list[Vertex]): Region to intersect

    Returns:
        list[Annotation]: Annotations that intersect with the region
    """
    def does_annotation_intersect(annotation: Annotation) -> bool:
        return does_region_intersect(annotation.bounds, region_vertices)

    annotations_in_region = list(filter(does_annotation_intersect, annotations))
    return annotations_in_region
