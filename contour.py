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

def create_line_string(vertices):
  tuple_points = []
  for v in vertices:
    tuple_points.append((v.x, v.y))
  return LineString(tuple_points)

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
  img = cv2.imread('/Users/ixistic/Desktop/test.jpg')
  img = cv2.resize(img, (int(img.shape[1] * 2), int(img.shape[0] * 2)))
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
  root_component = Component([], Polygon([(0, 0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]), "Main")
  root_area = root_component.polygon.area
  size_threshold = (0.1 / 100 * root_area)
  print "Size Threshold: " + str(size_threshold)

  for b,cnt in enumerate(contours):
    if hierarchy[0,b,3] == -1:
      approx = cv2.approxPolyDP(cnt, 0.015 * cv2.arcLength(cnt, True), True)
      vertices = get_vertices(approx)
      vertex_count = len(vertices)


      if (vertex_count == 1):
        # Ignore single dot
        continue
      if (vertex_count == 2):
        if (LineString([vertices[0], vertices[1]]).length > 100):
          draw(newimg, Component(vertices, Polygon(), ""), rand_color())
        pass      
      elif (vertex_count == 3):
        pass
      elif (vertex_count == 4):
        polygon = create_polygon(vertices)
        if polygon.area > size_threshold:
          components.append(Component(vertices, polygon, "Square#" + str(b)))
          pass
      elif (vertex_count == 5):
        polygon = create_polygon(vertices)
        if polygon.area > size_threshold:
          components.append(Component(vertices, polygon, "Pentagon#" + str(b)))
          pass
        pass
      elif (vertex_count == 6):
        pass
      elif (vertex_count == 7):
        pass
      elif (vertex_count == 8):
        pass
      else:
        point_x_max = max(vertices, key=lambda v: v.x)
        point_x_min = min(vertices, key=lambda v: v.x)
        point_y_max = max(vertices, key=lambda v: v.y)
        point_y_min = min(vertices, key=lambda v: v.y)
        # print [c.x for c in vertices]
        # vertices[0].x
        a = LineString([point_x_max, point_x_min])
        b = LineString([point_y_max, point_y_min])
        
        if(a.intersects(b)):
          point = a.intersection(b)
        
        length_all = []
        if(point.geom_type == "Point"):
          for v in vertices:
            length_all.append(create_line_string([point, v]).length)
          average = sum(length_all) / len(length_all)
          status = "true"
          for v in vertices:
            if (create_line_string([point, v]).length < average-4 or create_line_string([point, v]).length > average+4 ):
              status = "false"
          if (status == "true"):
            polygon = create_polygon(vertices)
            if (polygon.area >= 500):
              components.append(Component(vertices, polygon, "Circle"+str(polygon.area) ))
        pass
        # for v in vertices:
        #   print v.x

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