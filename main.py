import sys
import logging

from PyQt4 import QtGui
from gui import ImageDebuggerGUI
from processor import ElementDetector
from google import VisionAPI

is_gui_debugging = True

if __name__ == "__main__":

  logging.basicConfig(filename='out/debug.log',level=logging.DEBUG)
  logging.getLogger().addHandler(logging.StreamHandler())

  ocr = VisionAPI()
  detector = ElementDetector()
  detector.ocr = ocr

  if (is_gui_debugging):
    app = QtGui.QApplication(sys.argv)
    gui = ImageDebuggerGUI()
    detector.gui = gui

  print detector.detect("img/test7.jpg")
  
  if (is_gui_debugging):
    gui.show()
    sys.exit(app.exec_())
  