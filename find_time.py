import numpy as np
import argparse
import cv2


def read_image():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required = True,
		help = "Path to the image")
	args = vars(ap.parse_args())

	image = cv2.imread(args["image"])

	return image

def draw_circle(image):
	(centerX, centerY) = (image.shape[1] // 2, image.shape[0] // 2)
	white = (255, 255, 255)
	circSize = image.shape[0] // 15
	cv2.circle(image, (centerX, centerY), circSize, white, -1)
	cv2.imshow("With Circle", image)
	cv2.waitKey(0)

	return image

def parse_contours(image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (11, 11), 0)

	cv2.imshow("Image", image)
	cv2.imshow("Blurred", blurred)

	edged = cv2.Canny(blurred, 30, 150)
	cv2.imshow("Edges", edged)
	cv2.waitKey(0)

	(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	print("I count {} things in this image".format(len(cnts)))
	clock = image.copy()

	cv2.drawContours(image, cnts, -1, (0, 255, 0), 2)
	cv2.imshow("Contours", image)
	cv2.waitKey(0)

	return cnts


def find_sizes(image, cnts):
	sizes = []
	for (i, c) in enumerate(cnts):
		(x, y, w, h) = cv2.boundingRect(c)
		sizes.append(w**2 + h**2)
		
	max_val = -1
	max_index = -1
	for i in range(len(sizes)):
		if sizes[i] > max_val:
			max_val = sizes[i]
			max_index = i	

	print(sizes)
	print(max_val)
	c = cnts[max_index]
	(x, y, w, h) = cv2.boundingRect(c)
	clock_hand = image[y:y + h, x:x + w]
	print(x, y)
	print(h, w)
	cv2.imshow("Clock Hand", clock_hand)
	cv2.waitKey(0)

def main():
	image = read_image()
	draw_circle(image)
	cnts = parse_contours(image)
	find_sizes(image, cnts)

main()

# cv2.circle(mask, (int(centerX), int(centerY)), int(radius), 255, -1)
# mask = mask[y:y + h, x:x + w]
# cv2.imshow("Masked Thing", cv2.bitwise_and(coin, coin, mask = mask))
# cv2.waitKey(0)