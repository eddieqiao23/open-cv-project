# Reads Clock - OpenCV Project

This program takes a clock from [Time and Date](https://www.timeanddate.com/worldclock/) and uses OpenCV to find the time. 

Chapters used:
* Chapter 3 - Loads the image with imread
* Chapter 4 - Uses image[x, y] when differentiating between second and minute (line 116)
* Chapter 5 - Drew a white circle with cv2.circle() in the middle to separate the hands from each (line 21)
* Chapter 6 - Resized the image with cv2.resize() so it's easier to deal with (line 227), also mask with bitwise_and (line 65)
* Chapter 8 - Used cv2.GaussianBlur to make it easier to process the image (line 29)
* Chapter 10 - Used Canny Edge Detector with cv2.Canny() (line 30)
* Chapter 11 - Found contours with cv2.findContours() to find the hands and the numbers (line 33)

Note: clock10.png is an example of the program messing up. It doesn't happpen often, but with clock10, the hour and second hands are on top of each other, which messes it up. 