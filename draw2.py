
import sys
import numpy as np
import cv2
import random


img = np.zeros((200, 200, 3), np.uint8)
img[:,0.5*200:200] = (0,255,0)
cv2.line(img, (0, 0), (100, 100), (255, 0, 0), 1)
cv2.imshow('Show', img)
cv2.waitKey(0)
cv2.destroyAllWindows()


#       cv2.line(newimg, (vertex[g][0][y], vertex[g][0][y+1]), (vertex[g+1][0][y], vertex[g+1][0][y+1]), color, 2)
#       cv2.line(newimg, (vertex[len(vertex)-1][0][0], vertex[len(vertex)-1][0][1]), (vertex[0][0][0], vertex[0][0][1]), color, 2)

# img = cv2.imread('/Users/mapfap/Desktop/test.jpg')
# img = cv2.resize(img, (800, 400))
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# #Remove of noise, if any
# kernel = np.ones((2, 2),np.uint8)
# erosion = cv2.erode(gray, kernel, iterations = 1)

# #Create a new image of the same size of the starting image
# height, width = gray.shape
# newimg = np.zeros((height, width, 3), np.uint8)

# #Canny edge detector
# thresh = 240
# edges = cv2.Canny(erosion, thresh, thresh*2)

# contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
# # contours,hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# for b,cnt in enumerate(contours):
#   if hierarchy[0,b,3] == -1:
#     approx = cv2.approxPolyDP(cnt,0.015*cv2.arcLength(cnt,True), True)
#     r = random.randint(0, 255)
#     g = random.randint(0, 255)
#     b = random.randint(0, 255)
#     clr = (r, g, b)
#     print "Hey"
#     create_graph(approx, clr)

