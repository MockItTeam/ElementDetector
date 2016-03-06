import util
from shapely.geometry import Point
# from enum import Enum

SQUARE_THRESHOLD = 0.2

class Description:
  # Primary
  Unknown = "Unknown"

  Quadrilateral = "Quadrilateral"
  Triangle = "Triangle"

  # Secondary
  Square = "Square"
  Rectangle = "Rectangle"
  HorizontalRectangle = "HorizontalRectangle"
  VerticalRectangle = "VerticalRectangle"

  # Tertiary
  Root = "Root"
  TextField = "TextField"
  TextArea = "TextArea"
  Panel = "Panel"
  VideoPlayer = "VideoPlayer"
  Text = "Text"

class Element:
  def __init__(self, e_id, vertices, name):
    self.id = e_id
    self.vertices = vertices
    self.polygon = util.create_polygon(vertices)
    self.name = name
    self.children = []
    self.depth = 0
    # self.is_leaf = False
    self.description = Description.Unknown

    self.origin = Point(0, 0)
    self.width = 0
    self.height = 0

  def is_leaf(self):
    return len(self.children) == 0

  def add_child(self, child):
    self.children.append(child)

  def as_json(self):
    json = ""
    json += "{"
    json += '"id":' + str(self.id) + ","
    json += '"type":"' + self.description + '",'
    json += '"x":' + str(int(self.origin.x)) + ","
    json += '"y":' + str(int(self.origin.y)) + ","
    json += '"z":' + str(self.depth) + ","
    json += '"width":' + str(int(self.width)) + ","
    json += '"height":' + str(int(self.height)) + ","
    json += '"children_id":['
    for i in range(len(self.children)):
      if i != 0:
        json += ","
      json += str(self.children[i].id)
    json += "]"
    json += "}"
    return json

  @property
  def parent(self):
    return self.parent

  # @property
  # def area(self):
  #   return self.polygon.area

  # @property
  # def intersects(self):
  #   return self.polygon.intersects

  def is_a(self, description):
    # TODO: subclass equivalent
    return description == self.description

  def __lt__(self, other):
    return self.polygon.area < other.polygon.area

  def __str__(self):
    return "%s(%d)" % (self.name, self.polygon.area)

  def __repr__(self):
    return str(self)

  def __unicode__(self):
    return u"?"

class TextElement(Element):
  def __init__(self, e_id, vertices, name, text):
    Element.__init__(self, e_id, vertices, name)    
    self.description = Description.Text
    self.text = text

class TriangleElement(Element):
  def __init__(self, e_id, vertices, name):
    Element.__init__(self, e_id, vertices, name)

    if (len(vertices) != 3):
      raise Exception('TriangleElement', 'Need exactly 3 vertices')

    self.description = Description.Triangle

class QuadrilateralElement(Element):
  def __init__(self, e_id, vertices, name):
    Element.__init__(self, e_id, vertices, name)

    if (len(vertices) != 4):
      raise Exception('QuadrilateralElement', 'Need exactly 4 vertices')
    # self.describe = Geometry.Quadrilateral
    self.ratio = 0   # X-Parallel / Y-Parallel
    self.__describe()

  def __describe(self):
    self.description = Description.Quadrilateral

    side_1_axis = util.find_parallel_axis(self.vertices[0], self.vertices[1])
    side_2_axis = util.find_parallel_axis(self.vertices[1], self.vertices[2])
    side_3_axis = util.find_parallel_axis(self.vertices[2], self.vertices[3])
    side_4_axis = util.find_parallel_axis(self.vertices[3], self.vertices[0])

    # TODO: Describe other types e.g. Square

    if side_1_axis == side_3_axis and side_2_axis == side_4_axis and side_1_axis != side_2_axis:
      side1_len = self.vertices[0].distance(self.vertices[1])
      side2_len = self.vertices[1].distance(self.vertices[2])
      side3_len = self.vertices[2].distance(self.vertices[3])
      side4_len = self.vertices[3].distance(self.vertices[0])

      avg_13 = (side1_len + side3_len) / 2
      avg_24 = (side2_len + side4_len) / 2
      if side_1_axis == "x" and side_2_axis == "y":
        self.ratio = 1.0 * avg_13 / avg_24
        if avg_13 < avg_24:
          self.description = Description.VerticalRectangle
        else:
          self.description = Description.HorizontalRectangle
      elif side_1_axis == "y" and side_2_axis == "x":
        self.ratio = 1.0 * avg_24 / avg_13
        if avg_13 < avg_24:
          self.description = Description.HorizontalRectangle
        else:
          self.description = Description.VerticalRectangle
      
