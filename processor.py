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
      # if i != 0:
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

  def detect(self, filename):
    img = cv2.imread(filename)
    prefer_height = 1000
    img = cv2.resize(img, (int(1.0 * img.shape[1] * prefer_height / img.shape[0] ), prefer_height))
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (11, 11), 0)

    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 5)
    # src, result_intensity, method, type, block, area, weight_sum                   
    # cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    # cv2.THRESH_OTSU cv2.THRESH_BINARY
            
    img = cv2.bitwise_not(img)

    if self.gui:
      self.gui.show_image(0, img, 900)
    
    # kernel = np.ones((2, 2), np.uint8)
    # erosion = cv2.erode(img, kernel, iterations = 1)
    # erosion = img # Skip erosion

    height, width = img.shape
    newimg = np.zeros((height, width, 3), np.uint8)
    tmpimg = np.zeros((height, width, 3), np.uint8)
    redimg = np.zeros((height, width, 3), np.uint8)
    
    img = cv2.Canny(img, 128, 200) # min max

    # size = np.size(img)
    # skel = np.zeros(img.shape,np.uint8)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # # kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(100,100))
    # # kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(100,100))
    # # kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    # # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    # # kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    # # print kernel
    # done = False
     
    # while(not done):
    #   eroded = cv2.erode(img, kernel)      
    #   # cv2.imshow("",eroded)
    #   # cv2.waitKey(0)
    #   # cv2.destroyAllWindows()
    #   temp = cv2.dilate(eroded, kernel)
    #   temp = cv2.subtract(img, temp)
    #   skel = cv2.bitwise_or(skel, temp)
    #   img = eroded.copy()

    #   if cv2.countNonZero(img) == 0:
    #     done = True

    # img = skel
    if self.gui:
      self.gui.show_image(1, img, 900)

    # cv2.cv.CV_RETR_EXTERNAL cv2.cv.CV_RETR_LIST
    contours, hierarchy = cv2.findContours(img, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    elements = []
    root_element = Element(0, [Point(0, 0), Point(0, img.shape[0]), Point(img.shape[1], img.shape[0]), Point(img.shape[1], 0)], "Root")
    root_element.description = Description.Root
    root_area = root_element.polygon.area
    size_threshold = (0.05 / 100 * root_area)
    # print "Size Threshold: " + str(size_threshold)

    for number, cnt in enumerate(contours):
      if hierarchy[0, number, 3] == -1:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

        vertices = util.get_vertices(approx)
        vertex_count = len(vertices)

        if self.gui:
          self.gui.raw_draw(tmpimg, vertices, util.rand_color(), str(number))
        
        # Delete vertex that likely to be straight line
        vertices = util.reduce_vertex_by_length(vertices, 0.1)
        vertices = util.reduce_vertex_by_angle(vertices, 160)
        vertices = util.reduce_vertex_by_length(vertices, 0.2)
        vertices = util.reduce_vertex_by_angle(vertices, 145)
        vertices = util.reduce_vertex_by_length(vertices, 0.25)
        vertices = util.reduce_vertex_by_angle(vertices, 130)

        vertex_count = len(vertices)

        if (vertex_count == 0):
          continue
        if (vertex_count == 1):
          # Ignore single dot
          continue
        if (vertex_count == 2):
          # if (LineString([vertices[0], vertices[1]]).length > 100):
            # draw(newimg, Element(vertices, ""), rand_color())
          continue

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
        elif (vertex_count == 5):
          pass
        elif (vertex_count == 6):
          pass
        elif (vertex_count == 7):
          pass
        elif (vertex_count == 8):
          pass
        else:
          pass

    if self.gui:
      self.gui.show_image(2, tmpimg, 900)
    if self.gui:
      self.gui.show_image(3, redimg, 900)
    elements = util.remove_resembling_element(elements, 0.5)

    elements.append(root_element)
    elements.sort()

    ##### INITIATE TREE OPERATION !!

    # # print [c for c in elements]
    for i in range(len(elements)):
      for j in range(i + 1, len(elements)):
        if elements[i].polygon.within(elements[j].polygon):
          elements[i].parent = elements[j]
          elements[j].add_child(elements[i])
          # print "%s is in %s" % (elements[i].name, elements[j].name)
          break

    util.assign_depth(root_element)

    # for i in range(len(elements)):
      # c = elements[i]
      # if c.is_a(Description.Triangle):
        # destroy_all(c.children)

    self.destroy_all_children_of_triangle(root_element)

    self.detect_video_player(root_element)
    self.detect_panel(root_element)

    # TODO: Cannot do this anynore!! 
    for i in range(len(elements)):
      e = elements[i]
      if e.is_leaf:
        # describe_element(elements[i])
        if e.is_a(Description.HorizontalRectangle):
          if (e.ratio > 4):
            e.description = Description.TextField
          else:
            e.description = Description.TextArea
          e.name = e.description

    # for i in range(len(elements)):
      # if elements[i] is not None:
    if self.gui:
      self.gui.draw_tree(newimg, root_element)
    # cv2.imshow('Show', newimg)
    util.print_tree(root_element)
    
    if self.gui:
      self.gui.show_image(4, newimg, 900)

    json_result = ""
    json_result += "{"
    json_result += '"width":500,'
    json_result += '"height":500,'
    json_result += '"elements":['
    json_result += self.traverse_as_json(root_element)
    json_result += "]"
    json_result += "}"

    return json_result