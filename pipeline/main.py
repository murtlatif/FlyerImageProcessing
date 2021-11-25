import fitz
import argparse

from typing import Tuple
import os
import glob, sys

from flyer_preprocess import preprocess_img


def preprocess_flyer(flyer_path, override_existing=True):
    # Decrease file size
    zoom_x = 0.5  # horizontal zoom
    zoom_y = 0.5  # vertical zoom
    mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

    # path = "../input_data/metro"
    all_pdfs = glob.glob(flyer_path + "/*.pdf")
    valid_images = [".jpg", ".jpeg", ".png"]
    all_imgs = []
    for f in os.listdir(flyer_path):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        all_imgs.append(os.path.join(flyer_path, f))

    if not os.path.exists(flyer_path + "/out"):
        os.makedirs(flyer_path + "/out")
    else:
        if not override_existing:
            return

    if all_pdfs:
        for filename in all_pdfs:
            doc = fitz.open(filename)  # open document
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap(matrix=mat)  # render page to an image
                output_path = f"{flyer_path}/out/page-{page.number}.png"
                pix.save(output_path)  # store image as a PNG
                preprocess_img(output_path, f"{flyer_path}/out", "bilateral")
    if all_imgs:
        for img_path in all_imgs:
            filename = os.path.basename(img_path)
            output_path = f"{flyer_path}/out/"
            preprocess_img(img_path, output_path, "bilateral")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default="../input_data")
    parser.add_argument(
        "--override_existing",
        type=bool,
        help="If false, it will not preprocess an image if the out/ folder exists in the folder directory already",
        default=True,
    )
    args = parser.parse_args()

    if os.path.isfile(args.input_dir):
        preprocess_flyer(args.input_dir, args.override_existing)
    elif os.path.isdir(args.input_dir):
        for folder in os.listdir(args.input_dir):
            preprocess_flyer(
                os.path.join(args.input_dir, folder), args.override_existing
            )
