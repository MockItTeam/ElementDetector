import sys
import numpy as np
import cv2
import random
from shapely.geometry import Point, LineString, Polygon
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

def get_vertices(approx):
  vertices = []
  for i in range(len(approx)):
    vertices.append(Point(approx[i][0][0], approx[i][0][1]))
  return vertices

def draw(img, component, color):
  vertices = component.vertices

  vertex_count = len(vertices)
  for i in range(vertex_count - 1):
    cv2.circle(img, point_to_int_tuple(vertices[i]), 2, color, -1)
    # cv2.putText(img, str(i), vertices[i].xy, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    cv2.line(img, point_to_int_tuple(vertices[i]), point_to_int_tuple(vertices[i + 1]), color, 1)
  cv2.line(img, point_to_int_tuple(vertices[vertex_count - 1]), point_to_int_tuple(vertices[0]), color, 1) # Draw line from last vertex to the first one.
  
  # centroid = point_to_int_tuple(polygon.centroid)
  # cv2.circle(img, centroid, 1, color, -1)
  cv2.putText(img, component.name, point_to_int_tuple(vertices[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

def rand_color():
  r = random.randint(0, 255)
  g = random.randint(0, 255)
  b = random.randint(0, 255)
  return r, g, b

def main(argv):
  img = cv2.imread('img/test8.jpg')
  
  prefer_height = 800

  img = cv2.resize(img, (int(1.0 * img.shape[1] * prefer_height / img.shape[0] ), prefer_height))
  # img = cv2.resize(img, (int(img.shape[1] * 1.3), int(img.shape[0] * 1.3)))
  
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (7, 7), 0)

  # cv2.imshow('Show', gray)
  # cv2.waitKey(0)
  # cv2.destroyAllWindows()

  gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 5)
  # gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 3)
  #                            src   result_intensity   method             type            block area weight_sum                   

  # gray = cv2.GaussianBlur(gray, (7, 7), 0)


  # retval, gray = cv2.threshold(gray, 128, 255, cv2.THRESH_OTSU)

  # retval, gray = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

  cv2.imshow('Show', gray)
  cv2.waitKey(0)
  cv2.destroyAllWindows()


  # kernel = np.ones((2, 2), np.uint8)
  # erosion = cv2.erode(gray, kernel, iterations = 1)
  erosion = gray # Skip erosion

  height, width = gray.shape
  newimg = np.zeros((height, width, 3), np.uint8)

  # Canny edge detector
  # thresh = 128
  edges = cv2.Canny(erosion, 128, 200)
  #                           min max

  # cv2.imshow('Show', edges)
  # cv2.waitKey(0)
  # cv2.destroyAllWindows()

  # contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
  # contours, hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_LIST, cv2.cv.CV_CHAIN_APPROX_TC89_L1)
  # contours, hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


  components = []
  root_component = Component([], Polygon([(0, 0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]), "Main")
  root_area = root_component.polygon.area
  size_threshold = (0.1 / 100 * root_area)
  print "Size Threshold: " + str(size_threshold)

  for b, cnt in enumerate(contours):
    if False or hierarchy[0,b,3] == -1:
      print b
      print ":::\n"
      print cnt 
      print "~~~\n"
      approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
      

      vertices = get_vertices(approx)
      print [str(v.x) + "," + str(v.y) for v in vertices]

      print "!!!!\n"
      vertex_count = len(vertices)


      if (vertex_count == 1):
        # Ignore single dot
        continue
      if (vertex_count == 2):
        # if (LineString([vertices[0], vertices[1]]).length > 100):
          # draw(newimg, Component(vertices, Polygon(), ""), rand_color())
        continue      
      elif (vertex_count == 3):
        continue
      elif (vertex_count == 4):
        # if polygon.area > size_threshold:
        # polygon = create_polygon(vertices)
        # components.append(Component(vertices, polygon, "Square#" + str(b)))
        pass
      elif (vertex_count == 5):
        # polygon = create_polygon(vertices)
        # if polygon.area > size_threshold:
          # components.append(Component(vertices, polygon, "Pentagon#" + str(b)))
          # pass
        pass
      elif (vertex_count == 6):
        pass
      elif (vertex_count == 7):
        pass
      elif (vertex_count == 8):
        pass
      else:
        pass

      polygon = create_polygon(vertices)
      components.append(Component(vertices, polygon, ""))

  for c in components:
    draw(newimg, c, rand_color())

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