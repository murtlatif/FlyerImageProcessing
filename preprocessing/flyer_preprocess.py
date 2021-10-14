import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import cm
import os

for filename in os.listdir("sample_data"):
    if filename == ".DS_Store":
        continue
    img = cv2.imread(f"sample_data/{filename}")

    # Grey scale
    grey_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Black & white
    _, bw = cv2.threshold(grey_image, 127, 255, cv2.THRESH_BINARY)

    # Filtering

    # Sharpen img
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img_sharp = cv2.filter2D(src=bw, ddepth=-1, kernel=kernel)
    # _, img_sharp = cv2.threshold(img_sharp, 127, 255, cv2.THRESH_BINARY)

    # Blur img
    img_blur = cv2.blur(src=bw, ksize=(3, 3))

    # Bilateral filter
    bilateral_filter = cv2.bilateralFilter(src=bw, d=9, sigmaColor=75, sigmaSpace=75)

    # Thresholding
    th1 = cv2.adaptiveThreshold(
        img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    th2 = cv2.adaptiveThreshold(
        img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    cv2.imwrite(f"processed_data/bw_{filename}", bw)
    cv2.imwrite(f"processed_data/blur_{filename}", img_blur)
    cv2.imwrite(f"processed_data/bilateral_{filename}", bilateral_filter)
    cv2.imwrite(f"processed_data/sharp_{filename}", img_sharp)
    cv2.imwrite(f"processed_data/thresh1_{filename}", th1)
    cv2.imwrite(f"processed_data/thresh2_{filename}", th2)
