from typing import Sequence
from .ocr_annotation import OCRAnnotation
from .google_cloud import google_cloud_client
from .google_cloud.image_response import response_to_ocr_annotations, save_response_as_json


def get_text_annotations(file_image_path, save_file=None) -> Sequence[OCRAnnotation]:
    annotation_response = google_cloud_client.request_text_detection(file_image_path)

    if save_file:
        save_response_as_json(annotation_response, save_file)

    annotations = response_to_ocr_annotations(annotation_response)

    return annotations
