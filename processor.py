import sys
import numpy as np
import cv2
import util
import logging

from shapely.geometry import Point, LineString, Polygon
from element import *

class ElementDetector:

  def __init__(self):
    self.ocr = None
    self.gui = None

  def destroy_all_children(self, root):
    for i in range(len(root.children)):
      self.destroy_all_children(root.children[i])
      root.children[i] = None
    root.children = []

  def traverse_as_json(self, root):
    json = root.as_json()
    for i in range(len(root.children)):
      json += ","
      json += self.traverse_as_json(root.children[i])
    return json

  def destroy_all_children_of_triangle(self, root):
    if root.is_a(Description.Triangle):
      for i in range(len(root.children)):
        logging.info("Destroyed because its parent is Triangle: " + root.children[i].name)
      self.destroy_all_children(root)

    for c in root.children:
      self.destroy_all_children_of_triangle(c)

  def detect_video_player(self, root):
    if len(root.children) == 1 and root.is_a(Description.HorizontalRectangle) and root.children[0].is_a(Description.Triangle):
      root.description = Description.VideoPlayer
      logging.info("Found VideoPlayer Rect: %s and Tri: %s" % (root.name, root.children[0].name))
      root.name = root.description
      self.destroy_all_children(root)

    for c in root.children:
      self.detect_video_player(c)

  def detect_panel(self, root):
    if len(root.children) >= 1 and root.is_a(Description.HorizontalRectangle):
      root.description = Description.Panel
      root.name = root.description

    for c in root.children:
      self.detect_panel(c)

  def interpret_leaf_rectangle(self, root):
    if root.is_leaf():
      if root.is_a(Description.HorizontalRectangle):
        if (root.ratio > 4):
          root.description = Description.TextField
        else:
          root.description = Description.TextArea
        root.name = root.description
    
    for c in root.children:
      self.interpret_leaf_rectangle(c)

  def append_text_elements(self, filename, elements):
    pass
    # if self.ocr:
    #   response = self.ocr.detect_text(filename)
    #   logging.info(response)
    #   texts = response[0]["description"].split("\n")
    #   print texts
    #   print len(texts)
    #   for i in range(len(texts) - 1):
    #     text = texts[i]
    #     print text
    #     print i
    #     vertice = response[0]["boundingPoly"]["vertices"][i]
    #     x = vertice["x"]
    #     y = vertice["y"]

    #     # TODO: Generate Unique ID
    #     e_id = 999

    #     # TODO: Find proper size
    #     width = 10000
    #     height = 10000

    #     vertices = [Point(x, y), Point(x, y + height), Point(x + width, y + height), Point(x + width, 0)]
    #     element = TextElement(e_id, vertices, text, text)

  def detect(self, filename):
    img = cv2.imread(filename)
    prefer_height = 1000.0
    raw_height = img.shape[0]
    raw_width = img.shape[1]
    size_factor = prefer_height / raw_height
    img = cv2.resize(img, (int(raw_width * size_factor), int(prefer_height)))
    

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (11, 11), 0)

    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 5)
    # src, result_intensity, method, type, block, area, weight_sum                   
    # cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    # cv2.THRESH_OTSU cv2.THRESH_BINARY
            
    img = cv2.bitwise_not(img)

    if self.gui:
      self.gui.show_image(0, img, 900)
    
    height, width = img.shape
    newimg = np.zeros((height, width, 3), np.uint8)
    tmpimg = np.zeros((height, width, 3), np.uint8)
    redimg = np.zeros((height, width, 3), np.uint8)
    
    img = cv2.Canny(img, 128, 200) # min max

    if self.gui:
      self.gui.show_image(1, img, 900)

    # cv2.cv.CV_RETR_EXTERNAL cv2.cv.CV_RETR_LIST
    contours, hierarchy = cv2.findContours(img, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    elements = []
    root_element = Element(0, [Point(0, 0), Point(0, height), Point(width, height), Point(width, 0)], "Root")
    root_element.description = Description.Root
    root_area = root_element.polygon.area
    size_threshold = (0.05 / 100 * root_area)

    for number, cnt in enumerate(contours):
      if hierarchy[0, number, 3] == -1:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

        vertices = util.get_vertices(approx)
        vertex_count = len(vertices)

        if self.gui:
          self.gui.raw_draw(tmpimg, vertices, util.rand_color(), str(number))
        
        vertices = util.reduce_vertex_by_length(vertices, 0.1)
        vertices = util.reduce_vertex_by_angle(vertices, 160)
        vertices = util.reduce_vertex_by_length(vertices, 0.2)
        vertices = util.reduce_vertex_by_angle(vertices, 145)
        vertices = util.reduce_vertex_by_length(vertices, 0.25)
        vertices = util.reduce_vertex_by_angle(vertices, 130)

        vertex_count = len(vertices)

        if self.gui:
          self.gui.raw_draw(redimg, vertices, util.rand_color(), str(number))

        if (vertex_count == 3):
          e = TriangleElement(number, vertices, "Tri#" + str(number))
          if e.polygon.area > size_threshold:
            elements.append(e)
          continue
        elif (vertex_count == 4):
          e = QuadrilateralElement(number, vertices, "Quad#" + str(number))
          if e.polygon.area > size_threshold:
            elements.append(e)
          continue
        else:
          pass

    if self.gui:
      self.gui.show_image(2, tmpimg, 900)
    if self.gui:
      self.gui.show_image(3, redimg, 900)

    elements = util.remove_resembling_element(elements, 0.5)
    elements.append(root_element)
    
    self.append_text_elements(filename, elements)

    # START HANDLING ELEMENTS AS TREE
    util.construct_tree_by_within(elements)
    self.destroy_all_children_of_triangle(root_element)
    self.detect_video_player(root_element)
    self.detect_panel(root_element)
    self.interpret_leaf_rectangle(root_element)

    if self.gui:
      self.gui.draw_tree(newimg, root_element)

    util.print_tree(root_element)
    
    if self.gui:
      self.gui.show_image(4, newimg, 900)

    json_result = ""
    json_result += "{"
    json_result += '"width":' + str(width) + ','
    json_result += '"height":' + str(height) + ','
    json_result += '"elements":['
    json_result += self.traverse_as_json(root_element)
    json_result += "]"
    json_result += "}"

    return json_result