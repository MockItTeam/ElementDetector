import sys
import numpy as np
import cv2
import random
from shapely.geometry import Point, LineString, Polygon
from component import Component
from PyQt4 import QtCore, QtGui

class sliderdemo(QtGui.QWidget):
  def __init__(self, parent = None):
    super(sliderdemo, self).__init__(parent)

    # layout_a = QtGui.QVBoxLayout()

    layout = QtGui.QGridLayout()
    layout.setSpacing(10)

    # layout = QtGui.QHBoxLayout()
    # layout_a.addWidget(layout)

    self.l1 = QtGui.QLabel("Hello")
    self.l1.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(self.l1)

    self.sl = QtGui.QSlider(QtCore.Qt.Horizontal)
    self.sl.setMinimum(40)
    self.sl.setMaximum(100)
    self.sl.setValue(3)
    self.sl.setTickPosition(QtGui.QSlider.TicksBelow)
    self.sl.setTickInterval(1)
    layout.addWidget(self.sl, 0, 0)


    self.pic_labels = []

    for i in range(2):
      pic_label = QtGui.QLabel()
      pic_label.setGeometry(10, 10, 800, 800)
      layout.addWidget(pic_label, 1, i)
      self.pic_labels.append(pic_label)

    self.sl.valueChanged.connect(self.valuechange)
    self.setLayout(layout)
    self.setWindowTitle("SpinBox demo")

    self.process_image(0)
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

  def valuechange(self):
    val = self.sl.value()
    self.l1.setText(str(val))
    cv2.destroyAllWindows()

  def show_image(self, index, img):
    tmp = "out/ " + str(index) + ".jpg"
    cv2.imwrite(tmp, img)
    pixmap = QtGui.QPixmap(tmp)
    pixmap = pixmap.scaledToHeight(500)
    self.pic_labels[index].setPixmap(pixmap)

  def assign_depth(self, root):
    for c in root.children:
      c.depth = root.depth + 1
      self.assign_depth(c) 

  def print_tree(self, root, space = ""):
    print space + "- " + root.name + "_" +  str(root.depth)
    new_space = space + "-"
    for c in root.children:
      self.print_tree(c, new_space)

  def point_to_int_tuple(self, point):
    return int(point.x), int(point.y)

  def create_polygon(self, vertices):
    tuple_points = []
    for v in vertices:
      tuple_points.append((v.x, v.y))
    return Polygon(tuple_points)

  def get_vertices(self, approx):
    vertices = []
    for i in range(len(approx)):
      vertices.append(Point(approx[i][0][0], approx[i][0][1]))
    return vertices

  def draw(self, img, component, color):
    vertices = component.vertices

    vertex_count = len(vertices)
    for i in range(vertex_count - 1):
      cv2.circle(img, self.point_to_int_tuple(vertices[i]), 2, color, -1)
      # cv2.putText(img, str(i), vertices[i].xy, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
      cv2.line(img, self.point_to_int_tuple(vertices[i]), self.point_to_int_tuple(vertices[i + 1]), color, 1)
    cv2.line(img, self.point_to_int_tuple(vertices[vertex_count - 1]), self.point_to_int_tuple(vertices[0]), color, 1) # Draw line from last vertex to the first one.
    
    # centroid = self.point_to_int_tuple(polygon.centroid)
    # cv2.circle(img, centroid, 1, color, -1)
    cv2.putText(img, component.name, self.point_to_int_tuple(vertices[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

  def rand_color(self):
    r = 200#random.randint(0, 255)
    g = 205#random.randint(0, 255)
    b = 0#random.randint(0, 255)
    return r, g, b

  def process_image(self, val):
    img = cv2.imread('img/test9.jpg')
    prefer_height = 1000
    img = cv2.resize(img, (int(1.0 * img.shape[1] * prefer_height / img.shape[0] ), prefer_height))
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)

    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 3)
    # src, result_intensity, method, type, block, area, weight_sum                   
    # cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    # cv2.THRESH_OTSU cv2.THRESH_BINARY
            
    self.show_image(0, gray)

    # kernel = np.ones((2, 2), np.uint8)
    # erosion = cv2.erode(gray, kernel, iterations = 1)
    erosion = gray # Skip erosion

    height, width = gray.shape
    newimg = np.zeros((height, width, 3), np.uint8)

    
    edges = cv2.Canny(erosion, 128, 200) # min max
    
    # self.show_image(0, edges)


    # cv2.cv.CV_RETR_EXTERNAL cv2.cv.CV_RETR_LIST
    contours,hierarchy = cv2.findContours(edges, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    components = []
    root_component = Component([], Polygon([(0, 0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]), "Main")
    root_area = root_component.polygon.area
    size_threshold = (0.1 / 100 * root_area)
    # print "Size Threshold: " + str(size_threshold)

    for b, cnt in enumerate(contours):
      if hierarchy[0,b,3] == -1:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

        vertices = self.get_vertices(approx)
        vertex_count = len(vertices)

        if (vertex_count == 1):
          # Ignore single dot
          continue
        if (vertex_count == 2):
          # if (LineString([vertices[0], vertices[1]]).length > 100):
            # draw(newimg, Component(vertices, Polygon(), ""), rand_color())
          continue      
        elif (vertex_count == 3):
          print 
          continue
        elif (vertex_count == 4):
          # if polygon.area > size_threshold:
          # polygon = create_polygon(vertices)
          # components.append(Component(vertices, polygon, "Square#" + str(b)))
          pass
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

        polygon = self.create_polygon(vertices)
        components.append(Component(vertices, polygon, ""))

    for c in components:
      self.draw(newimg, c, self.rand_color())
    # components.append(root_component)
    # components.sort()
    
    # # print [c for c in components]
    # for i in range(len(components)):
    #   for j in range(i + 1, len(components)):
    #     if components[i].polygon.within(components[j].polygon):
    #       components[j].add_child(components[i])
    #       # print "%s is in %s" % (components[i].name, components[j].name)
    #       break

    # self.assign_depth(root_component)
    # self.print_tree(root_component)

    # cv2.imshow('Show', newimg)
    self.show_image(1, newimg)

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  ex = sliderdemo()
  ex.show()
  sys.exit(app.exec_())
  # main(sys.argv)