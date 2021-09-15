import numpy as np
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "Path to the image")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (11, 11), 0)

cv2.imshow("Image", image)
cv2.imshow("Blurred", blurred)

edged = cv2.Canny(blurred, 30, 150)
cv2.imshow("Edges", edged)
cv2.waitKey(0)
