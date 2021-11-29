import os.path

import ocr.google_cloud.annotation_response
from config import Config
from ocr.annotation_types import AnnotationLevel
from ocr.display_bounds import draw_hierarchical_annotations
from ocr.get_annotations import get_text_annotations


def draw_boxes_around_text(image_path: str, annotation_json_path: str):
    image_file_name = os.path.basename(image_path)
    image_file_without_ext, _ = os.path.splitext(image_file_name)

    if annotation_json_path:
        response = ocr.google_cloud.annotation_response.load_response_from_json(annotation_json_path)
        annotations = ocr.google_cloud.annotation_response.response_to_hierarchical_annotations(response)
    else:
        annotations = get_text_annotations(image_path, save_file=image_file_without_ext, hierarchical=True)

    bounded_image = draw_hierarchical_annotations(
        image_path, annotations=annotations, annotation_level_whitelist={AnnotationLevel.BLOCK})
    bounded_image.save(f'bounded_{image_file_without_ext}.png')


if __name__ == '__main__':
    pass

    # draw_boxes_around_text(r'data\4589_no-frills-atlantic-flyer-september-30-to-october-6_page_4.png',
    #                        r'data\ocr_annotations\4589_no-frills-atlantic-flyer-september-30-to-october-6_page_4.json')
