import sys
import numpy as np
import cv2
import random
from shapely.geometry import Point, Polygon
from component import Component

def assign_depth(root):
  for c in root.children:
    c.depth = root.depth + 1
    assign_depth(c) 

def print_tree(root, space = ""):
  print space + "- " + root.name + "_" +  str(root.depth)
  new_space = space + "-"
  for c in root.children:
    print_tree(c, new_space)


def point_to_int_tuple(point):
  return int(point.x), int(point.y)

def create_polygon(vertices):
  tuple_points = []
  for v in vertices:
    tuple_points.append((v.x, v.y))
  return Polygon(tuple_points)

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

def draw(img, vertices, color, polygon, name):
  vertex_count = len(vertices)
  for i in range(vertex_count - 1):
    cv2.circle(img, point_to_int_tuple(vertices[i]), 2, color, -1)
    # cv2.putText(img, str(i), vertices[i].xy, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    cv2.line(img, point_to_int_tuple(vertices[i]), point_to_int_tuple(vertices[i + 1]), color, 1)
  cv2.line(img, point_to_int_tuple(vertices[vertex_count - 1]), point_to_int_tuple(vertices[0]), color, 1) # Draw line from last vertex to the first one.
  
  # centroid = point_to_int_tuple(polygon.centroid)
  # cv2.circle(img, centroid, 1, color, -1)
  cv2.putText(img, name, point_to_int_tuple(vertices[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

def rand_color():
  r = random.randint(0, 255)
  g = random.randint(0, 255)
  b = random.randint(0, 255)
  return r, g, b

def main(argv):
  img = cv2.imread('/Users/mapfap/Desktop/test.jpg')
  img = cv2.resize(img, (int(img.shape[1] * 1), int(img.shape[0] * 1)))
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  kernel = np.ones((2, 2), np.uint8)
  erosion = cv2.erode(gray, kernel, iterations = 1)
  # erosion = gray # Skip erosion

  height, width = gray.shape
  newimg = np.zeros((height, width, 3), np.uint8)

  # Canny edge detector
  thresh = 180
  edges = cv2.Canny(erosion, thresh, thresh * 2)

  contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
  # contours,hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  components = []

  for b,cnt in enumerate(contours):
    if hierarchy[0,b,3] == -1:
      approx = cv2.approxPolyDP(cnt, 0.015 * cv2.arcLength(cnt, True), True)
      vertices = get_vertices(approx)
      area = polygon_area(vertices)
      vertex_count = len(vertices)
      # print "area=%d, vertices=%d" % (area, len(vertices))
      will_draw = False
      if (vertex_count == 1):
        pass
      elif (vertex_count == 2):
        pass
      elif (vertex_count == 3):
        pass
      elif (vertex_count == 4):
        polygon = create_polygon(vertices)
        if polygon.area > 100:
          will_draw = True
        # print polygon.centroid
          components.append(Component(polygon, "Square#"+ str(b)))
          
          # print "a=%d" % (component.area)
        pass
      elif (vertex_count == 5):
        pass
      elif (vertex_count == 6):
        pass
      elif (vertex_count == 7):
        pass
      elif (vertex_count == 8):
        # will_draw = True
        pass
      else:
        pass
      
      if (will_draw):
        draw(newimg, vertices, rand_color(), polygon, "SQUARE " + str(b))
  root_component = Component(Polygon([(0, 0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]), "Main")
  components.append(root_component)
  components.sort()
  print [c for c in components]
  for i in range(len(components)):
    for j in range(i + 1, len(components)):
      # print "%d.%d" % (i, j)
      if components[i].polygon.within(components[j].polygon):
        components[j].add_child(components[i])
        print "%s is in %s" % (components[i].name, components[j].name)
        break
      # else:
        # print "%s isn't in %s" % (components[i].name, components[j].name)

  assign_depth(root_component)
  print_tree(root_component)

  cv2.imshow('Show', newimg)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main(sys.argv)