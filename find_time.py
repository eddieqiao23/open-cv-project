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
	circSize = image.shape[0] // 10
	cv2.circle(image, (centerX, centerY), circSize, white, -1)
	# cv2.imshow("With Circle", image)
	# cv2.waitKey(0)

	return image

def parse_contours(image):
	imageCopy = image.copy()
	# Uses Canny to blur the images and finds the contours
	gray = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (3, 3), 0)

	# cv2.imshow("Image", image)
	# cv2.imshow("Blurred", blurred)

	edged = cv2.Canny(blurred, 30, 150)
	# cv2.imshow("Edges", edged)
	# cv2.waitKey(0)

	(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	# print(cnts)

	cv2.drawContours(imageCopy, cnts, -1, (0, 255, 0), 2)
	cv2.imshow("Contours", imageCopy)
	cv2.waitKey(0)

	# for c in cnts:
	# 	(x, y, w, h) = cv2.boundingRect(c)
	# 	coin = image[y:y + h, x:x + h]
	# 	cv2.imshow("Coin", coin)
	# 	cv2.waitKey(0)

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
	# Finds the closest and farthest points on the numbers
	# min_distances = []
	# max_distances = []
	for (i, c) in enumerate(cnts):
		if sizes[i] < 5000:
			# minDist = 100000000
			# maxDist = 0
			for j in range(len(cnts[i])):
				(x, y) = cnts[i][j][0]
				centerDist = (x - centerX)**2 + (y - centerY)**2
				minDist = min(minDist, centerDist)
				maxDist = max(maxDist, centerDist)
			# min_distances.append(minDist)
			# max_distances.append(maxDist)
	# print(max_distances)	
	print(maxDist)
	print(minDist)

	(centerX, centerY) = (image.shape[1] // 2, image.shape[0] // 2)
	white = (255, 255, 255)

	# Uses a mask to get the inside part
	insideCircSize = int(minDist**(1/2))
	mask = np.zeros(image.shape[:2], dtype = "uint8")
	cv2.circle(mask, (centerX, centerY), insideCircSize, 255, -1)
	insideOnly = cv2.bitwise_and(image, image, mask = mask)

	# Makes everything outside of the inside white (maybe optimize with masks later)
	for x in range(image.shape[1]):
		for y in range(image.shape[0]):
			if (x - centerX)**2 + (y - centerY)**2 > insideCircSize**2:
				insideOnly[y, x] = (255, 255, 255)

	cv2.imshow("Inside Only", insideOnly)

	insideAngles = find_inside_angles(insideOnly)

	outsideCircSize = int(maxDist**(1/2)) + 2
	outsideOnly = image.copy()
	cv2.circle(outsideOnly, (centerX, centerY), outsideCircSize, white, -1)
	cv2.imshow("Outside circle", outsideOnly)

	cv2.imshow("Original", image)

	cv2.waitKey(0)
	
	outsideAngles = find_outside_angles(outsideOnly)

	print(outsideAngles)
	print(insideAngles)
	for (i, outsideAngle) in enumerate(outsideAngles):
		for j in range(len(insideAngles)):
			if abs(insideAngles[j] - outsideAngle) < 10:
				if i == 0:
					minAngle = insideAngles[j]
				else:
					secAngle = insideAngles[j]
				break
	
	hourAngle = 0
	for insideAngle in insideAngles:
		hourAngle += insideAngle
	if len(insideAngles) == 2:
		hourAngle *= 3 / 2
	elif len(insideAngles) == 1:
		hourAngle *= 3
	hourAngle -= minAngle + secAngle

	print(hourAngle, minAngle, secAngle)

	hourTime = math.floor(hourAngle / 360 * 12)
	minTime = round(minAngle / 360 * 60)
	secTime = round(secAngle / 360 * 60)
	
	print("%d:%d:%d" % (hourTime, minTime, secTime))


def find_inside_angles(insideOnly):
	# Adds each of the hands and uses find_angle to calculate the angles
	cnts = parse_contours(insideOnly)

	coords = []
	for hand in cnts:
		(x, y, w, h) = cv2.boundingRect(hand)
		coords.append([x, y, w, h])
	
	angles = []
	for i in range(len(coords)):
		handAngle = find_angle(insideOnly, coords[i][0], coords[i][1], coords[i][2], coords[i][3])
		angles.append(handAngle)

	return angles

def find_outside_angles(outsideOnly):
	cnts = parse_contours(outsideOnly)

	# Minute then second
	coords = []
	for hand in cnts:
		# Finds the average rgb to determine second vs. minute
		(x, y, w, h) = cv2.boundingRect(hand)
		r_avg = 0
		b_avg = 0
		g_avg = 0
		for x_val in range(x, x + w):
			for y_val in range(y, y + h):
				(b, g, r) = outsideOnly[y_val, x_val]
				r_avg += r
				b_avg += b
				g_avg += g 
		
		r_avg /= (w * h)
		b_avg /= (w * h)
		g_avg /= (w * h)

		coords.append([x + w / 2, y + h / 2, r_avg, b_avg, g_avg])

	# Makes it minute then second by swapping
	if coords[0][2] > coords[1][2]:
		temp = coords[0]
		coords[0] = coords[1]
		coords[1] = temp

	(centerX, centerY) = (outsideOnly.shape[1] // 2, outsideOnly.shape[0] // 2)
	# Look through the two hands and find the angle
	angles = []
	for i in range(2):
		# Calculate x, y, w, h to use find_angle
		(handX, handY) = (coords[i][0], coords[i][1])
		handBoxX = min(handX, centerX)
		handBoxY = min(handY, centerY)
		handBoxW = max(handX, centerX) - handBoxX
		handBoxH = max(handY, centerY) - handBoxY
		handAngle = find_angle(outsideOnly, handBoxX, handBoxY, handBoxW, handBoxH)
		angles.append(handAngle)

	return angles
	# cv2.imshow("Outside Only", outsideOnly)
	# cv2.waitKey(0)

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
	bx = 2 * x + w - ax
	by = 2 * y + h - ay

	slope = -(by - ay) / (bx - ax)

	angle = np.arctan(slope)
	angle = angle * 180 / math.pi

	top_angle = 90 - angle
	if quadrant == 3 or quadrant == 4:
		top_angle += 180

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