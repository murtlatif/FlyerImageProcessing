import os.path

import ocr.google_cloud.image_response
from config import Config
from ocr.display_bounds import draw_text_annotations
from ocr.recognize import get_text_annotations


def draw_box_around_sign():
    image_path = Config.args.img
    annotation_json_path = Config.args.annotations
    if annotation_json_path:
        response = ocr.google_cloud.image_response.load_response_from_json(annotation_json_path)
        annotations = ocr.google_cloud.image_response.response_to_ocr_annotations(response)
    else:
        image_file_name = os.path.basename(image_path)
        image_file_without_ext, _ = os.path.splitext(image_file_name)
        annotations = get_text_annotations(image_path, save_file=image_file_without_ext)

    draw_text_annotations(image_path, annotations=annotations)


if __name__ == '__main__':
    draw_box_around_sign()
