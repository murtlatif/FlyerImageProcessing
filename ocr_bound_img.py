import os.path

import ocr.google_cloud.annotation_response
from config import Config
from ocr.display_bounds import draw_text_annotations
from ocr.get_annotations import get_text_annotations


def draw_boxes_around_text():
    image_path = Config.args.image_path
    image_file_name = os.path.basename(image_path)
    image_file_without_ext, _ = os.path.splitext(image_file_name)

    annotation_json_path = Config.args.annotations_file

    if annotation_json_path:
        response = ocr.google_cloud.annotation_response.load_response_from_json(annotation_json_path)
        annotations = ocr.google_cloud.annotation_response.response_to_flat_annotations(response)
    else:
        annotations = get_text_annotations(image_path, save_file=image_file_without_ext)

    bounded_image = draw_text_annotations(image_path, annotations=annotations)
    bounded_image.save(f'bounded_{image_file_without_ext}.png')


if __name__ == '__main__':
    draw_boxes_around_text()
