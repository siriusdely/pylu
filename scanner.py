# import necessary packages
from transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils

# construct the argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

# load the image and compute the ratio of the old height to the new height,
# clone and resize it
image = cv2.imread(args["image"])
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height=500)

# convert the image to grayscale, blur it, and find edges
# in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)

# show the original image and the edge detected image
print("STEP 1: Edge Detection")
cv2.imshow("Image", image)
cv2.imshow("Gray", gray)
cv2.imshow("Edged", edged)

# find the contours in the edges image, keeping only the
# largest ones, and initialize the screen contour
contours = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(contours)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

# loop over the contours
for contour in contours:
    # approximate the contour
    perimeter = cv2.arcLength(contour, True)
    approximate = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

    # if our approximated contour has four points, then we
    # can assume that we have found our screen
    if len(approximate) == 4:
        screenContour = approximate
        break

# show the contour (outline) of the piece of paper
print("STEP 2: Find the contours of paper")
cv2.drawContours(image, [screenContour], -1, (0, 255, 0), 2)
cv2.imshow("Outline", image)

# apply the four point transform to obtain a top-down
# view of the original image
warped = four_point_transform(orig, screenContour.reshape(4, 2) * ratio)

# convert the warped image to grayscale, then threshold it
# to give it that 'black and white' paper effect
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
T = threshold_local(warped, 11, offset=10, method="gaussian")
warped = (warped > T).astype("uint8") * 255

# show the original and scanned images
print("STEP 3: Apply perspective transform")
cv2.imshow("Original", imutils.resize(orig, height=650))
cv2.imshow("Scanned", imutils.resize(warped, height=650))

cv2.waitKey(0)
cv2.destroyAllWindows()
