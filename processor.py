import sys
import numpy as np
import cv2
import util
import logging

from shapely.geometry import Point, LineString, Polygon
from component import *

class ElementDetector:

  def __init__(self, gui):
    self.gui = gui

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
    self.gui.show_image(1, img, 900)

    # cv2.cv.CV_RETR_EXTERNAL cv2.cv.CV_RETR_LIST
    contours, hierarchy = cv2.findContours(img, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    components = []
    root_component = Component(0, [Point(0, 0), Point(0, img.shape[0]), Point(img.shape[1], img.shape[0]), Point(img.shape[1], 0)], Polygon([(0, 0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]), "Root")
    root_component.description = Description.Root
    root_area = root_component.polygon.area
    size_threshold = (0.05 / 100 * root_area)
    # print "Size Threshold: " + str(size_threshold)

    for b, cnt in enumerate(contours):
      if hierarchy[0,b,3] == -1:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

        vertices = util.get_vertices(approx)
        vertex_count = len(vertices)

        self.gui.raw_draw(tmpimg, vertices, util.rand_color(), str(b))
        
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
            # draw(newimg, Component(vertices, Polygon(), ""), rand_color())
          continue

        self.gui.raw_draw(redimg, vertices, util.rand_color(), str(b))

        if (vertex_count == 3):
          polygon = util.create_polygon(vertices)
          # if not polygon.is_valid:
          #   continue
          if polygon.area > size_threshold:
            components.append(TriangleComponent(b, vertices, polygon, "Tri#" + str(b)))
          continue
        elif (vertex_count == 4):
          polygon = util.create_polygon(vertices)
          # if not polygon.is_valid:
          #   continue
          if polygon.area > size_threshold:
            c = QuadrilateralComponent(b, vertices, polygon, "Quad#" + str(b))
            # c.name = c.geometry_type + str(c.ratio)
            components.append(c)
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

        # polygon = util.create_polygon(vertices)
        # if polygon.area > size_threshold:
          # components.append(Component(vertices, polygon, "X"))

    self.gui.show_image(2, tmpimg, 900)
    self.gui.show_image(3, redimg, 900)
    components = util.remove_resembling_component(components, 0.5)

    components.append(root_component)
    components.sort()

    ##### INITIATE TREE OPERATION !!

    # # print [c for c in components]
    for i in range(len(components)):
      for j in range(i + 1, len(components)):
        if components[i].polygon.within(components[j].polygon):
          components[i].parent = components[j]
          components[j].add_child(components[i])
          # print "%s is in %s" % (components[i].name, components[j].name)
          break

    util.assign_depth(root_component)

    # for i in range(len(components)):
      # c = components[i]
      # if c.is_a(Description.Triangle):
        # destroy_all(c.children)

    self.destroy_all_children_of_triangle(root_component)

    self.detect_video_player(root_component)
    self.detect_panel(root_component)

    # TODO: Cannot do this anynore!! 
    for i in range(len(components)):
      c = components[i]
      if c.is_leaf:
        # describe_component(components[i])
        if c.is_a(Description.HorizontalRectangle):
          if (c.ratio > 4):
            c.description = Description.TextField
          else:
            c.description = Description.TextArea
          c.name = c.description
          # print c.name

    # for i in range(len(components)):
      # if components[i] is not None:
    self.gui.draw_tree(newimg, root_component)
    # cv2.imshow('Show', newimg)
    util.print_tree(root_component)
    
    self.gui.show_image(4, newimg, 900)

    json_result = ""
    json_result += "{"
    json_result += '"width":500,'
    json_result += '"height":500,'
    json_result += '"elements":['
    json_result += self.traverse_as_json(root_component)
    json_result += "]"
    json_result += "}"
    return json_result