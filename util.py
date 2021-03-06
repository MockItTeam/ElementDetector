import math
import random
import sys
import logging

from shapely.geometry import Point, LineString, Polygon
from element import Element

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]

def clean_cos(cos_angle):
  return min(1, max(cos_angle, -1))

def find_angle_from_x_axis(p1, p2):
  delta_y = p2.y - p1.y
  delta_x = p2.x - p1.x
  if delta_x == 0:
    return 90
  angle = math.atan(delta_y / delta_x) / math.pi * 180
  # if angle < 0:
    # return 180 + angle
  # else:
  return angle

def find_parallel_axis(p1, p2):
  angle = find_angle_from_x_axis(p1, p2)
  if abs(angle) < 30:
    return "x"
  elif abs(angle) < 60:
    return ""
  else:
    return "y"

def all_are(items, description):
  for item in items:
    if item.description != description:
      return False
  return True

def find_angle(a, vertex, b):
  # angle(Point(0,-1), Point(0,0), Point(0,1))
  # print "%d %d %d %d %d %d" % (a.x, a.y, vertex.x, vertex.y, b.x, b.y)
  vec_a = [(vertex.x - a.x), (vertex.y - a.y)]
  vec_b = [(vertex.x - b.x), (vertex.y - b.y)]
  # Get dot prod
  dot_prod = dot(vec_a, vec_b)
  # Get magnitudes
  mag_a = dot(vec_a, vec_a) ** 0.5
  mag_b = dot(vec_b, vec_b) ** 0.5
  # Get cosine value
  cos_ = dot_prod / mag_a / mag_b
  # Get angle in radians and then convert to degrees
  # print "%d %d %d" % (dot_prod, mag_a, mag_b)
  angle = math.acos(clean_cos(dot_prod / mag_b / mag_a))
  # Basically doing angle <- angle mod 360
  ang_deg = math.degrees(angle) % 360

  if ang_deg - 180 >= 0:
    return 360 - ang_deg
  else: 
    return ang_deg

def min_max_vertices(vertices):
  min_x = vertices[0].x
  min_y = vertices[0].y
  max_x = vertices[0].x
  max_y = vertices[0].y
  for v in vertices:
    if v.x < min_x:
      min_x = v.x
    if v.x > max_x:
      max_x = v.x
    if v.y < min_y:
      min_y = v.y
    if v.y > max_y:
      max_y = v.y

  return min_x, min_y, max_x, max_y

def reduce_vertex_by_length(vertices, threshold):
  
  vertex_count = len(vertices)
  if vertex_count >= 2:
    for i in range(vertex_count):
      if vertices[i].distance(vertices[(i + 1) % vertex_count]) < threshold:
          vertices.pop(i)
          return reduce_vertex_by_length(vertices, threshold)
  return vertices

def reduce_vertex_by_average_length(vertices, threshold):
  # vertices = list(vertices)
  # out = []
  vertex_count = len(vertices)
  if vertex_count >= 2:

    average = 0
    for i in range(vertex_count):
      average += vertices[i].distance(vertices[(i + 1) % vertex_count])
    average /= vertex_count

    # max_val = -1
    # for i in range(vertex_count):
    #   val = vertices[i].distance(vertices[(i + 1) % vertex_count])
    #   if val > max_val:
    #     max_val = val

    for i in range(vertex_count):
      if vertices[i].distance(vertices[(i + 1) % vertex_count]) < threshold * average:
        vertices.pop(i)
        return reduce_vertex_by_average_length(vertices, threshold)

  # out = vertices
  return vertices

def reduce_vertex_by_angle(vertices, threshold):
  out = []
  vertex_count = len(vertices)
  # print "--- %d" % (vertex_count)
  if vertex_count >= 3:
    for i in range(vertex_count):
      a = vertices[(i - 1) % vertex_count]
      vertex = vertices[i]
      b = vertices[(i + 1) % vertex_count]

      # if a == vertex or vertex == b or b == a:
        # return []
      angle = find_angle(a, vertex, b)
      if angle > threshold:
        # print angle
        pass
      else:
        out.append(vertices[i])
      # print angle

  return out

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

def get_bounding_vertices(vertices):
  if len(vertices) == 0:
    return []
  padding = 20
  min_x = min(vertices, key=lambda v: v.x).x - padding
  min_y = min(vertices, key=lambda v: v.y).y - padding
  max_x = max(vertices, key=lambda v: v.x).x + padding
  max_y = max(vertices, key=lambda v: v.y).y + padding
  return [Point(min_x, min_y), Point(min_x, max_y), Point(max_x, max_y), Point(max_x, min_y)]

def rand_color():
  # r = random.randint(0, 255)
  # g = random.randint(0, 255)
  # b = random.randint(0, 255)
  # return r, g, b
  return 255,100,0

def construct_tree_by_within(elements):
  elements.sort()
  for i in range(len(elements)):
    for j in range(i + 1, len(elements)):
      if elements[i].polygon.within(elements[j].polygon):
        elements[i].parent = elements[j]
        elements[j].add_child(elements[i])
        # print "%s is in %s" % (elements[i].name, elements[j].name)
        break

def assign_depth(root):
  # if len(root.children) == 0:
    # root.is_leaf = True
  for c in root.children:
    c.depth = root.depth + 1
    assign_depth(c) 

def print_tree(root, space = ""):
  logging.info(space + "- " + root.name + "_" +  str(root.depth) + ("~" if root.is_leaf() else ""))
  new_space = space + "-"
  for c in root.children:
    print_tree(c, new_space)

def remove_resembling_element(elements, threshold):
  for i in range(len(elements)):
    for j in range(i+1, len(elements)):
      if (is_resembling_subset(elements[i].polygon, elements[j].polygon, threshold)):
        logging.info("Remove resembling element: " + elements[i].name)
        elements.pop(i)
        return remove_resembling_element(elements, threshold)
  return elements

def is_resembling_subset(a, b, threshold):
  # if not (a.is_valid and b.is_valid):
  return False

  if a.area > b.area:
    bigger = a
    smaller = b
  else:
    bigger = b
    smaller = a

  if smaller.within(bigger):
    intersect_area = bigger.intersection(smaller).area
    union_area = bigger.union(smaller).area
    if intersect_area > threshold * union_area:
      return True
    else:
      return False
  else:
    return False

#If b upper a then return true
def is_upper(vertices_a,vertices_b):
  point_y_min_a = min(vertices_a, key=lambda v: v.y)
  point_y_max_b = max(vertices_b, key=lambda v: v.y)
  return point_y_max_b < point_y_min_a

#If b lower a then return true
def is_lower(vertices_a,vertices_b):
  point_y_max_a = max(vertices_a, key=lambda v: v.y)
  point_y_min_b = min(vertices_b, key=lambda v: v.y)
  return point_y_max_a < point_y_min_b

#If b left a then return true
def is_left(vertices_a,vertices_b):
  point_x_min_a = min(vertices_a, key=lambda v: v.x)
  point_x_max_b = max(vertices_b, key=lambda v: v.x)
  return point_x_min_a > point_x_max_b

#If b right a then return true
def is_right(vertices_a,vertices_b):
  point_x_max_a = max(vertices_a, key=lambda v: v.x)
  point_x_min_b = min(vertices_b, key=lambda v: v.x)
  return point_x_max_a < point_x_min_b

#If b upper-left a then return true
def is_upper_left(vertices_a,vertices_b):
  return is_upper(vertices_a,vertices_b) and is_left(vertices_a,vertices_b)

#If b upper-left a then return true
def is_upper_right(vertices_a,vertices_b):
  return is_upper(vertices_a,vertices_b) and is_right(vertices_a,vertices_b) 

#If b upper-left a then return true
def is_lower_left(vertices_a,vertices_b):
  return is_lower(vertices_a,vertices_b) and is_left(vertices_a,vertices_b)

#If b upper-left a then return true
def is_lower_right(vertices_a,vertices_b):
  return is_lower(vertices_a,vertices_b) and is_right(vertices_a,vertices_b)
