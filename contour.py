import sys
import numpy as np
import cv2
import random
from point import Point

def polygon_area(vertices):
  n = len(vertices)
  area = 0.0
  for i in range(n):
    j = (i + 1) % n
    area += vertices[i].x * vertices[j].y
    area -= vertices[j].x * vertices[i].y
  area = abs(area) / 2.0
  return area

def get_vertices(approx):
  vertices = []
  for i in range(len(approx)):
    vertices.append(Point(approx[i][0][0], approx[i][0][1]))
  return vertices

def draw(img, vertices, color):
  vertex_count = len(vertices)
  for i in range(vertex_count - 1):
    cv2.circle(img, vertices[i].tuple(), 2, color, -1)
    cv2.line(img, vertices[i].tuple(), vertices[i+1].tuple(), color, 1)
  cv2.line(img, vertices[vertex_count - 1].tuple(), vertices[0].tuple(), color, 1) # Draw line from last vertex to the first one.

def rand_color():
  r = random.randint(0, 255)
  g = random.randint(0, 255)
  b = random.randint(0, 255)
  return r, g, b

def main(argv):
  img = cv2.imread('/Users/mapfap/Desktop/test3.jpg')
  img = cv2.resize(img, (int(img.shape[1]*0.5), int(img.shape[0]*0.5)))
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  # kernel = np.ones((2, 2), np.uint8)
  # erosion = cv2.erode(gray, kernel, iterations = 1)
  erosion = gray # Skip erosion

  height, width = gray.shape
  newimg = np.zeros((height, width, 3), np.uint8)

  # Canny edge detector
  thresh = 0
  edges = cv2.Canny(erosion, thresh, thresh*2)

  contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
  # contours,hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  for b,cnt in enumerate(contours):
    if hierarchy[0,b,3] == -1:
      approx = cv2.approxPolyDP(cnt,0.015*cv2.arcLength(cnt,True), True)
      vertices = get_vertices(approx)
      area = polygon_area(vertices)
      print "area=%d, vertices=%d" % (area, len(vertices))
      draw(newimg, vertices, rand_color())

  cv2.imshow('Show', newimg)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main(sys.argv)