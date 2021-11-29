import fitz
from util.file_path_util import (apply_default_file_ext,
                                 get_file_name_without_ext)


def convert_pdf_to_image(pdf_path: str, extension: str = '.png'):
    """
    Converts a PDF file to an image. Valid image file extensions are `.png`,
    `.jpg` and `.jpeg`.

    Raises:
        ValueError: The extension given is not a valid file extension.

    Returns:
        list[str]: The list of file output names
    """

    if extension not in {'.png', '.jpg', '.jpeg'}:
        raise ValueError(f'"{extension}" is not a valid image extension.')

    # Decrease file size
    zoom_x = 0.5  # horizontal zoom
    zoom_y = 0.5  # vertical zoom

    mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

    pdf_document = fitz.open(pdf_path)

    output_file_paths: list[str] = []

    for pdf_page in pdf_document:
        pixmap = pdf_page.get_pixmap(matrix=mat)

        file_name_without_ext = get_file_name_without_ext(pdf_path)
        output_image_file_name = f'{file_name_without_ext}_page{pdf_page}'
        output_image_path = apply_default_file_ext(output_image_file_name, extension, force=True)

        pixmap.save(output_image_path)

        output_file_paths.append(output_image_path)

    return output_file_paths
