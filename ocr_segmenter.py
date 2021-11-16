from config import Config
from flyer.flyer_types import Flyer
from flyer.marshal_flyer import marshal_flyer
from ocr.annotation_types import OCRAnnotation
from ocr.get_annotations import get_text_annotations
from ocr.ocr_segmentation import segment_page


def segment_with_ocr(annotations: list[OCRAnnotation]):
    segmented_page = segment_page(annotations)
    flyer = Flyer(
        pages=[
            segmented_page,
        ]
    )

    marshal_flyer(flyer, 'test_segmentation')
    return flyer


if __name__ == '__main__':
    ocr_annotations = get_text_annotations(
        annotation_json_path=Config.args.annotations_file,
        file_image_path=Config.args.image_path,
        request_as_fallback=Config.args.request_ocr,
    )

    segment_with_ocr(ocr_annotations)
