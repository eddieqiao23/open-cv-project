import numpy as np
import argparse
import cv2
import math


def read_image():
	# Reads the image
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required = True,
		help = "Path to the image")
	args = vars(ap.parse_args())

	image = cv2.imread(args["image"])

	return image

def draw_circle(image):
	# Draws a white circle in the middle
	(centerX, centerY) = (image.shape[1] // 2, image.shape[0] // 2)
	white = (255, 255, 255)
	circSize = image.shape[0] // 15
	cv2.circle(image, (centerX, centerY), circSize, white, -1)
	# cv2.imshow("With Circle", image)
	# cv2.waitKey(0)

	return image

def parse_contours(image):
	# Uses Canny to blur the images and finds the contours
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (11, 11), 0)

	# cv2.imshow("Image", image)
	# cv2.imshow("Blurred", blurred)

	edged = cv2.Canny(blurred, 30, 150)
	# cv2.imshow("Edges", edged)
	# cv2.waitKey(0)

	(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# print(cnts)

	cv2.drawContours(image, cnts, -1, (0, 255, 0), 2)
	cv2.imshow("Contours", image)
	cv2.waitKey(0)

	return cnts


def find_sizes(image, cnts):
	(centerX, centerY) = (image.shape[1] // 2, image.shape[0] // 2)
	sizes = []
	# Goes through the contours and adds the size of the bounding box
	for c in cnts:
		(x, y, w, h) = cv2.boundingRect(c)
		sizes.append(w**2 + h**2)
		
		
	# print(sizes)
	minDist = 100000000
	maxDist = 0
	print(cnts[0][0])
	# Finds the closest and farthest points on the numbers
	for (i, c) in enumerate(cnts):
		if sizes[i] < 5000:
			for j in range(len(cnts[i])):
				(x, y) = cnts[i][j][0]
				centerDist = (x - centerX)**2 + (y - centerY)**2
				minDist = min(minDist, centerDist)
				maxDist = max(maxDist, centerDist)

	print("minDist:", minDist)

	# Draws a circle inside and outside the numbers
	(centerX, centerY) = (image.shape[1] // 2, image.shape[0] // 2)
	white = (255, 255, 255)
	circSize = int(minDist**(1/2))
	cv2.circle(image, (centerX, centerY), circSize, white, -1)
	cv2.imshow("Inside circle", image)

	circSize2 = int(maxDist**(1/2)) + 2
	cv2.circle(image, (centerX, centerY), circSize2, white, -1)
	cv2.imshow("Outside circle", image)
	cv2.waitKey(0)

	min_index = -1
	min_val = -1
	sec_index = -1
	sec_val = -1
	hour_val = -1
	hour_index = -1
	# Finds the first, second, and third biggest hands
	for i in range(len(sizes)):
		if sizes[i] > min_val:
			min_val = sizes[i]
			min_index = i
	
	min_found = False
	for i in range(len(sizes)):
		if min_val == sizes[i] and not(min_found):
			min_found = True
			continue
		if sizes[i] > sec_val:
			sec_val = sizes[i]
			sec_index = i

	min_found = False
	sec_found = False
	for i in range(len(sizes)):
		if min_val == sizes[i] and not(min_found):
			min_found = True
			continue
		if sec_val == sizes[i] and not(sec_found):
			sec_found = True
			continue
		if sizes[i] > hour_val:
			hour_val = sizes[i]
			hour_index = i

	
	# for i in range(len(sizes)):
	# 	if sizes[i] > min_val:
	# 		hour_val = sec_val
	# 		hour_index = sec_index 
	# 		sec_val = min_val 
	# 		sec_index = min_index	
	# 		min_val = sizes[i]
	# 		min_index = i
	# 	elif sizes[i] > sec_val:
	# 		hour_val = sec_val
	# 		hour_index = sec_index 
	# 		sec_val = sizes[i]
	# 		sec_index = i
	# 	elif sizes[i] > hour_val:
	# 		hour_val = sizes[i]
	# 		hour_index = i
			
	min_pts = cnts[min_index]
	(mx, my, mw, mh) = cv2.boundingRect(min_pts)
	min_hand = image[my:my + mh, mx:mx + mw]
	# cv2.imshow("Minute Hand", min_hand)
	# cv2.waitKey(0)

	sec_pts = cnts[sec_index]
	(sx, sy, sw, sh) = cv2.boundingRect(sec_pts)
	sec_hand = image[sy:sy + sh, sx:sx + sw]
	# cv2.imshow("Second Hand", sec_hand)
	# cv2.waitKey(0)

	hour_pts = cnts[hour_index]
	(hx, hy, hw, hh) = cv2.boundingRect(hour_pts)
	hour_hand = image[hy:hy + hh, hx:hx + hw]
	# cv2.imshow("Hour Hand", hour_hand)
	# cv2.waitKey(0)

	# Finds the angles and outputs them
	min_angle = find_angle(image, mx, my, mw, mh)
	sec_angle = find_angle(image, sx, sy, sw, sh)
	hour_angle = find_angle(image, hx, hy, hw, hh)
	
	print("minute is", min_angle / 360 * 60)
	print("second is", sec_angle / 360 * 60)
	print("hour is", hour_angle / 360 * 12)

def find_angle(image, x, y, w, h):
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
	closestVal = 100000000
	optimalAx = -1
	optimalAy = -1
	ax_index = 0
	ay_index = 0
	for ax in x_vals:
		ax_index += 1
		ay_index = 0
		for ay in y_vals:
			ay_index += 1
			if (centerX - ax)**2 + (centerY - ay)**2 < closestVal:
				quadrant = ax_index * 2 + ay_index - 2
				closestVal = (centerX - ax)**2 + (centerY - ay)**2
				optimalAx = ax
				optimalAy = ay

	ax = optimalAx
	ay = optimalAy
	print(quadrant)
	bx = 2 * x + w - ax
	by = 2 * y + h - ay
	print(x, y, w, h)
	print(ax, ay, bx, by, quadrant)

	slope = -(by - ay) / (bx - ax)
	print("slope:", slope)

	angle = np.arctan(slope)
	angle = angle * 180 / math.pi
	print("angle:", angle)

	top_angle = 90 - angle
	if quadrant == 3 or quadrant == 4:
		top_angle += 180

	print("top_angle:", top_angle)
	print("\n\n")
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