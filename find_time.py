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

(centerX, centerY) = (image.shape[1] // 2, image.shape[0] // 2)
white = (255, 255, 255)
cv2.circle(image, (centerX, centerY), 30, white, -1)

(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print("I count {} things in this image".format(len(cnts)))
clock = image.copy()

for (i, c) in enumerate(cnts):
	(x, y, w, h) = cv2.boundingRect(c)
	
	print("Thing #{}".format(i + 1))
	coin = image[y:y + h, x:x + w]
	cv2.imshow("Coin", coin)
	cv2.waitKey(0)
	
	mask = np.zeros(image.shape[:2], dtype = "uint8")
	((centerX, centerY), radius) = cv2.minEnclosingCircle(c)

cv2.circle(mask, (int(centerX), int(centerY)), int(radius), 255, -1)
mask = mask[y:y + h, x:x + w]
cv2.imshow("Masked Thing", cv2.bitwise_and(coin, coin, mask = mask))
cv2.waitKey(0)