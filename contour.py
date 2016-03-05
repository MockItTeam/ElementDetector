import sys
import numpy as np
import cv2
import util

from shapely.geometry import Point, LineString, Polygon
from component import *

from PyQt4 import QtCore, QtGui

class ImgProc(QtGui.QWidget):
  def __init__(self, parent = None):
    super(ImgProc, self).__init__(parent)

    # layout_a = QtGui.QVBoxLayout()

    group_box = QtGui.QGroupBox('this is my groupbox')
    grid_layout = QtGui.QGridLayout()
    grid_layout.setSpacing(10)
    group_box.setLayout(grid_layout)
    # layout = QtGui.QHBoxLayout()
    # layout_a.addWidget(layout)

    # self.l1 = QtGui.QLabel("Threshold")
    # self.l1.setAlignment(QtCore.Qt.AlignCenter)
    # layout.addWidget(self.l1)

    # self.sl = QtGui.QSlider(QtCore.Qt.Horizontal)
    # self.sl.setMinimum(40)
    # self.sl.setMaximum(100)
    # self.sl.setValue(3)
    # self.sl.setTickPosition(QtGui.QSlider.TicksBelow)
    # self.sl.setTickInterval(1)
    # layout.addWidget(self.sl, 0, 0)

    scroll_area = QtGui.QScrollArea()
    scroll_area.setWidget(group_box)
    scroll_area.setWidgetResizable(True)
    scroll_area.setFixedWidth(1200)
    scroll_area.setFixedHeight(800)
    
    layout = QtGui.QVBoxLayout(self)
    layout.addWidget(scroll_area)

    self.pic_labels = []

    for i in range(5):
      pic_label = QtGui.QLabel()
      pic_label.setGeometry(10, 10, 100, 100)
      grid_layout.addWidget(pic_label, 5 - i, 0)
      self.pic_labels.append(pic_label)

    # self.sl.valueChanged.connect(self.valuechange)
    self.setLayout(layout)
    self.setWindowTitle("Debug IMG")

    self.process_image(0)
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

  def mouseReleaseEvent(self, QMouseEvent):
    # cursor = QtGui.QCursor()
    sys.exit(0)

  def valuechange(self):
    val = self.sl.value()
    self.l1.setText(str(val))
    cv2.destroyAllWindows()

  def show_image(self, index, img, height):
    tmp = "out/ " + str(index) + ".jpg"
    cv2.imwrite(tmp, img)
    pixmap = QtGui.QPixmap(tmp)
    pixmap = pixmap.scaledToHeight(height)
    self.pic_labels[index].setPixmap(pixmap)

  def draw_tree(self, root):
    self.draw(self.newimg, root, util.rand_color())
    for c in root.children:
      self.draw_tree(c)

  def destroy_all_children(self, root):
    for i in range(len(root.children)):
      self.destroy_all_children(root.children[i])
      root.children[i] = None
    root.children = []

  def destroy_all_children_of_triangle(self, root):
    if root.is_a(Description.Triangle):
      for i in range(len(root.children)):
        print "Destroyed because its parent is Triangle: " + root.children[i].name
      self.destroy_all_children(root)

    for c in root.children:
      self.destroy_all_children_of_triangle(c)

  def detect_video_player(self, root):

    if len(root.children) == 1 and root.is_a(Description.HorizontalRectangle) and root.children[0].is_a(Description.Triangle):
      root.description = Description.VideoPlayer
      print "Found VideoPlayer Rect: %s and Tri: %s" % (root.name, root.children[0].name)
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

  def draw(self, img, component, color):
    vertices = component.vertices

    vertex_count = len(vertices)
    for i in range(vertex_count):
      cv2.circle(img, util.point_to_int_tuple(vertices[i]), 3, color, -1)
      # cv2.putText(img, str(i), vertices[i].xy, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
      cv2.line(img, util.point_to_int_tuple(vertices[i]), util.point_to_int_tuple(vertices[(i + 1) % vertex_count]), color, 1)

    # centroid = util.point_to_int_tuple(polygon.centroid)
    # cv2.circle(img, centroid, 1, color, -1)
    cv2.putText(img, component.description, util.point_to_int_tuple(vertices[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

  def raw_draw(self, img, vertices, color, tag):
    vertex_count = len(vertices)
    for i in range(vertex_count):
      cv2.circle(img, util.point_to_int_tuple(vertices[i]), 3, color, -1)
      cv2.line(img, util.point_to_int_tuple(vertices[i]), util.point_to_int_tuple(vertices[(i + 1) % vertex_count]), color, 1)
    cv2.putText(img, tag, util.point_to_int_tuple(vertices[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

  def process_image(self, val):
    img = cv2.imread('img/test10.jpg')
    prefer_height = 1000
    img = cv2.resize(img, (int(1.0 * img.shape[1] * prefer_height / img.shape[0] ), prefer_height))
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (11, 11), 0)

    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 5)
    # src, result_intensity, method, type, block, area, weight_sum                   
    # cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    # cv2.THRESH_OTSU cv2.THRESH_BINARY
            
    img = cv2.bitwise_not(img)

    self.show_image(0, img, 900)
    

    # kernel = np.ones((2, 2), np.uint8)
    # erosion = cv2.erode(img, kernel, iterations = 1)
    # erosion = img # Skip erosion

    height, width = img.shape
    self.newimg = np.zeros((height, width, 3), np.uint8)
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
    self.show_image(1, img, 900)



    # self.show_image(0, img)


    # cv2.cv.CV_RETR_EXTERNAL cv2.cv.CV_RETR_LIST
    contours, hierarchy = cv2.findContours(img, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    components = []
    root_component = Component([Point(0, 0), Point(0, img.shape[0]), Point(img.shape[1], img.shape[0]), Point(img.shape[1], 0)], Polygon([(0, 0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]), "Root")
    root_area = root_component.polygon.area
    size_threshold = (0.05 / 100 * root_area)
    # print "Size Threshold: " + str(size_threshold)

    for b, cnt in enumerate(contours):
      if hierarchy[0,b,3] == -1:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

        vertices = util.get_vertices(approx)
        vertex_count = len(vertices)

        self.raw_draw(tmpimg, vertices, util.rand_color(), str(b))
        
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
            # draw(self.newimg, Component(vertices, Polygon(), ""), rand_color())
          continue

        self.raw_draw(redimg, vertices, util.rand_color(), str(b))

        if (vertex_count == 3):
          polygon = util.create_polygon(vertices)
          # if not polygon.is_valid:
          #   continue
          if polygon.area > size_threshold:
            components.append(TriangleComponent(vertices, polygon, "Tri#" + str(b)))
          continue
        elif (vertex_count == 4):
          polygon = util.create_polygon(vertices)
          # if not polygon.is_valid:
          #   continue
          if polygon.area > size_threshold:
            c = QuadrilateralComponent(vertices, polygon, "Quad#" + str(b))
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

    self.show_image(2, tmpimg, 900)
    self.show_image(3, redimg, 900)
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
    self.draw_tree(root_component)
    # cv2.imshow('Show', self.newimg)
    util.print_tree(root_component)
    self.show_image(4, self.newimg, 900)

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  ui = ImgProc()
  ui.show()
  sys.exit(app.exec_())
  # main(sys.argv)