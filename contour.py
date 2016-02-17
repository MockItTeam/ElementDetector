import sys
import numpy as np
import cv2

def create_graph(vertex, color):
  for g in range(0, len(vertex)-1):
    for y in range(0, len(vertex[0][0])-1):
      cv2.circle(newimg, (vertex[g][0][y], vertex[g][0][y+1]), 3, (255,255,255), -1)
      cv2.line(newimg, (vertex[g][0][y], vertex[g][0][y+1]), (vertex[g+1][0][y], vertex[g+1][0][y+1]), color, 2)
      cv2.line(newimg, (vertex[len(vertex)-1][0][0], vertex[len(vertex)-1][0][1]), (vertex[0][0][0], vertex[0][0][1]), color, 2)

img = cv2.imread('ooi.jpg')
img = cv2.resize(img, (800, 400))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#Remove of noise, if any
kernel = np.ones((2, 2),np.uint8)
erosion = cv2.erode(gray, kernel, iterations = 1)

#Create a new image of the same size of the starting image
height, width = gray.shape
newimg = np.zeros((height, width, 3), np.uint8)

#Canny edge detector
thresh = 175
edges = cv2.Canny(erosion, thresh, thresh*2)

# contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
contours,hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for b,cnt in enumerate(contours):
  if hierarchy[0,b,3] == -1:
    approx = cv2.approxPolyDP(cnt,0.015*cv2.arcLength(cnt,True), True)
    clr = (255, 0, 0)
    create_graph(approx, clr)

cv2.imshow('Show', newimg)
cv2.waitKey(0)
cv2.destroyAllWindows()