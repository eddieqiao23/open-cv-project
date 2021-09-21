import numpy as np
import argparse
import cv2
import math


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
	(mx, my, mw, mh) = cv2.boundingRect(c)
	clock_hand = image[my:my + mh, mx:mx + mw]
	cv2.imshow("Clock Hand", clock_hand)
	cv2.waitKey(0)

	min_angle = find_angle(image, mx, my, mw, mh)
	
	print("minute is", min_angle / 360 * 60)

def find_angle(image, x, y, w, h):
	print(image.shape[1])
	(centerX, centerY) = (image.shape[1] // 2, image.shape[0] // 2)
	quadrant = -1
	nearCenter = image.shape[0] // 10
	# Checks which of the edges is near the center to determine quadrant
	# 4 2
	# 3 1
	# ax, ay, bx, by
	x_vals = [x, x + w]
	y_vals = [y, y + h]
	quadrant = 0 
	found = False
	for ax in x_vals:
		for ay in y_vals:
			quadrant += 1
			if (centerX - ax)**2 + (centerY - ay)**2 < nearCenter**2:
				found = True
				break

		if found:
			break

	bx = 2 * x + w - ax
	by = 2 * y + h - ay
	print(ax, ay, bx, by, quadrant)

	slope = -(by - ay) / (bx - ax)
	print(slope)

	angle = np.arctan(slope)
	angle = angle * 180 / math.pi
	print(angle * 180 / math.pi)

	top_angle = 90 - angle
	print(top_angle)
	if quadrant == 3 or quadrant == 4:
		top_angle += 180

	print(top_angle)
	return top_angle

def main():
	image = read_image()
	r = 500.0 / image.shape[0]
	dim = (int(image.shape[1] * r), 500)
	image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

	draw_circle(image)
	cnts = parse_contours(image)
	find_sizes(image, cnts)
	


main()