
import sys
import numpy as np
import cv2
import random
import math

def PolygonArea(corners):
  n = len(corners) # of corners
  area = 0.0
  for i in range(n):
    j = (i + 1) % n
    area += corners[i][0] * corners[j][1]
    area -= corners[j][0] * corners[i][1]
  area = abs(area) / 2.0
  return area

def dist(x1,x2,y1,y2):
  return math.hypot(x2 - x1, y2 - y1)

def create_graph(vertex, color):
  if len(vertex) >= 7:
    corners = []

    for g in range(0, len(vertex)-1):
      corners.append( (vertex[g][0][0], vertex[g][0][1]) )

    distance = []
    num_sum = 0
    for x in range(0, len(corners)-1):
      distance.append(dist(corners[x][0],corners[x+1][0],corners[x][1],corners[x+1][1]))
      num_sum += dist(corners[x][0],corners[x+1][0],corners[x][1],corners[x+1][1])
      print dist(corners[x][0],corners[x+1][0],corners[x][1],corners[x+1][1])

    # distance.append(dist(corners[0][0],corners[len(corners)-1][0],corners[0][1],corners[len(corners)-1][1]))
    # print dist(corners[0][0],corners[len(corners)-1][0],corners[0][1],corners[len(corners)-1][1])
    if (len(corners)-1 != 0):
      average = num_sum/(len(corners)-1)
    print "ice"

    area = PolygonArea(corners)
    if (area > 100):
      status = "yes"
      for c in range(0, len(distance)-1):
        if(int(distance[c]) < int(average)-4 | int(distance[c]) > int(average)+4):
          status = "no"

      if(status == "yes"):    
        for g in range(0, len(vertex)-1):
          # for y in range(0, len(vertex[0][0])-1):
          # [0][0] is X
          # [0][1] is Y
          dista = dist(corners[g][0],corners[g+1][0],corners[g][1],corners[g+1][1])
          corners.append( (vertex[g][0][0], vertex[g][0][1]) );
          cv2.circle(newimg, (vertex[g][0][0], vertex[g][0][1]), 2, color, -1)
          cv2.line(newimg, (vertex[g][0][0], vertex[g][0][1]), (vertex[g+1][0][0], vertex[g+1][0][1]), color, 1)
        cv2.line(newimg, (vertex[len(vertex)-1][0][0], vertex[len(vertex)-1][0][1]), (vertex[0][0][0], vertex[0][0][1]), color, 1)
  # print vertex
  # print len(vertex)


img = cv2.imread('/Users/ixistic/Desktop/test.jpg')
img = cv2.resize(img, (800, 400))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#Remove of noise, if any
kernel = np.ones((2, 2),np.uint8)
erosion = cv2.erode(gray, kernel, iterations = 1)

#Create a new image of the same size of the starting image
height, width = gray.shape
newimg = np.zeros((height, width, 3), np.uint8)

#Canny edge detector
thresh = 0
edges = cv2.Canny(erosion, thresh, thresh*2)

contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
# contours,hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for b,cnt in enumerate(contours):
  if hierarchy[0,b,3] == -1:
    approx = cv2.approxPolyDP(cnt,0.015*cv2.arcLength(cnt,True), True)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    clr = (r, g, b)
    create_graph(approx, clr)

cv2.imshow('Show', newimg)
cv2.waitKey(0)
cv2.destroyAllWindows()