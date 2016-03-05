import sys
import numpy as np
import cv2
import util

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

    for i in range(3):
      pic_label = QtGui.QLabel()
      pic_label.setGeometry(10, 10, 100, 100)
      layout.addWidget(pic_label, 1, i)
      self.pic_labels.append(pic_label)

    self.sl.valueChanged.connect(self.valuechange)
    self.setLayout(layout)
    self.setWindowTitle("SpinBox demo")

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

  def draw(self, img, component, color):
    vertices = component.vertices

    vertex_count = len(vertices)
    for i in range(vertex_count):
      cv2.circle(img, util.point_to_int_tuple(vertices[i]), 3, color, -1)
      # cv2.putText(img, str(i), vertices[i].xy, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
      cv2.line(img, util.point_to_int_tuple(vertices[i]), util.point_to_int_tuple(vertices[(i + 1) % vertex_count]), color, 1)

    # centroid = util.point_to_int_tuple(polygon.centroid)
    # cv2.circle(img, centroid, 1, color, -1)
    cv2.putText(img, component.name, util.point_to_int_tuple(vertices[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

  def process_image(self, val):
    img = cv2.imread('img/test8.jpg')
    prefer_height = 1000
    img = cv2.resize(img, (int(1.0 * img.shape[1] * prefer_height / img.shape[0] ), prefer_height))
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (11, 11), 0)

    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 5)
    # src, result_intensity, method, type, block, area, weight_sum                   
    # cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    # cv2.THRESH_OTSU cv2.THRESH_BINARY
            
    img = cv2.bitwise_not(img)

    self.show_image(0, img, 200)
    

    # kernel = np.ones((2, 2), np.uint8)
    # erosion = cv2.erode(img, kernel, iterations = 1)
    # erosion = img # Skip erosion

    height, width = img.shape
    newimg = np.zeros((height, width, 3), np.uint8)

    
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
    self.show_image(1, img, 200)



    # self.show_image(0, img)


    # cv2.cv.CV_RETR_EXTERNAL cv2.cv.CV_RETR_LIST
    contours, hierarchy = cv2.findContours(img, cv2.cv.CV_RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    components = []
    root_component = Component([], Polygon([(0, 0), (0, img.shape[0]), (img.shape[1], img.shape[0]), (img.shape[1], 0)]), "Main")
    root_area = root_component.polygon.area
    size_threshold = (0.05 / 100 * root_area)
    # print "Size Threshold: " + str(size_threshold)

    for b, cnt in enumerate(contours):
      if hierarchy[0,b,3] == -1:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

        vertices = util.get_vertices(approx)
        vertex_count = len(vertices)

        # Delete vertex that likely to be straight line
        vertices = util.reduce_vertex_by_length(vertices, 0.2)
        vertices = util.reduce_vertex_by_angle(vertices, 140)
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
        elif (vertex_count == 3):
          polygon = util.create_polygon(vertices)
          if polygon.area > size_threshold:
            components.append(Component(vertices, polygon, "Tri"))
        elif (vertex_count == 4):
          polygon = util.create_polygon(vertices)
          if polygon.area > size_threshold:
            components.append(Component(vertices, polygon, "Rec"))
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

        # polygon = util.create_polygon(vertices)
        # components.append(Component(vertices, polygon, ""))

    for c in components:

      self.draw(newimg, c, util.rand_color())
    # components.append(root_component)
    # components.sort()
    
    # # print [c for c in components]
    # for i in range(len(components)):
    #   for j in range(i + 1, len(components)):
    #     if components[i].polygon.within(components[j].polygon):
    #       components[j].add_child(components[i])
    #       # print "%s is in %s" % (components[i].name, components[j].name)
    #       break

    # util.assign_depth(root_component)
    # util.print_tree(root_component)

    # cv2.imshow('Show', newimg)
    self.show_image(2, newimg, 900)

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  ex = sliderdemo()
  ex.show()
  sys.exit(app.exec_())
  # main(sys.argv)