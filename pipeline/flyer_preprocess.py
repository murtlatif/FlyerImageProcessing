import cv2
import numpy as np
import os
import argparse


def preprocess_img(input_dir, o, p_type):
    filename = os.path.basename(input_dir)
    if filename == ".DS_Store":
        return

    img = cv2.imread(input_dir)

    # Grey scale
    grey_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Black & white
    _, bw = cv2.threshold(grey_image, 127, 255, cv2.THRESH_BINARY)

    if p_type == "bw":
        cv2.imwrite(f"{o}/preprocessed_{filename}", bw)
        return

    # Filtering

    # Sharpen img
    if p_type == "sharp":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img_sharp = cv2.filter2D(src=bw, ddepth=-1, kernel=kernel)
        cv2.imwrite(f"{o}/preprocessed_{filename}", img_sharp)
        return

    # Blur img
    img_blur = cv2.blur(src=bw, ksize=(3, 3))
    if p_type == "blur":
        cv2.imwrite(f"{o}/preprocessed_{filename}", img_blur)
        return

    # Bilateral filter
    if p_type == "bilateral":
        bilateral_filter = cv2.bilateralFilter(
            src=bw, d=9, sigmaColor=75, sigmaSpace=75
        )
        cv2.imwrite(f"{o}/preprocessed_{filename}", bilateral_filter)
        return

    if p_type == "thresh":
        th = cv2.adaptiveThreshold(
            img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        cv2.imwrite(f"{o}/preprocessed_{filename}", th)
        return

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default="../fake_data/sample_data")
    parser.add_argument("--o", type=str, default="../fake_data/processed_data")
    parser.add_argument(
        "--p_type",
        type=str,
        help="Preprocess type: bilateral (default), bw (black and white), sharp (sharpen), blur, thresh (thresholding)",
        default="bilateral",
    )
    args = parser.parse_args()

    if os.path.isfile(args.input_dir):
        preprocess_img(args.input_dir, args.o, args.p_type)
    elif os.path.isdir(args.input_dir):
        for filename in os.listdir(args.input_dir):
            preprocess_img(os.path.join(args.input_dir, filename), args.o, args.p_type)
