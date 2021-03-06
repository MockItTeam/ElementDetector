import cv2
import util
import os

class StepDebugger:
  def __init__(self):
    self.active = False

  def log(self, img):
    pass

  def draft_vertices(self, img, vertices, color):
   pass

  def draw_vertices(self, img, vertices, color, tag):
    pass

  def log_vertices(self, img, vertices, color, tag):
    pass

class FileWriterStepDebugger(StepDebugger):
  def __init__(self):
    StepDebugger.__init__(self)
    self.active = True
    self.count = 0
    self.directory = "/tmp/mockit-step"
    if not os.path.exists(self.directory):
      os.makedirs(self.directory)

  def log(self, img):
    self.count += 1
    tmp = (self.directory + "/{0:05d}.jpg").format(self.count)
    cv2.imwrite(tmp, img)

  def draft_vertices(self, img, vertices, color):
    vertex_count = len(vertices)
    if vertex_count == 0:
      return
    for i in range(vertex_count):
      cv2.circle(img, util.point_to_int_tuple(vertices[i]), 3, color, -1)
      cv2.line(img, util.point_to_int_tuple(vertices[i]), util.point_to_int_tuple(vertices[(i + 1) % vertex_count]), color, 1)

  def draw_vertices(self, img, vertices, color, tag):
    vertex_count = len(vertices)
    if vertex_count == 0:
      return
    for i in range(vertex_count):
      cv2.circle(img, util.point_to_int_tuple(vertices[i]), 3, color, -1)
      cv2.line(img, util.point_to_int_tuple(vertices[i]), util.point_to_int_tuple(vertices[(i + 1) % vertex_count]), color, 1)
    cv2.putText(img, tag, (int(vertices[i].x) + 10, int(vertices[i].y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

  def log_vertices(self, img, vertices, color, tag):
    self.draw_vertices(img, vertices, color, tag)
    self.log(img)

