import sys
import logging
import argparse

from PyQt4 import QtGui
from gui import ImageDebuggerGUI
from processor import ElementDetector
from google import VisionAPI

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--debug", help="Enable console debugging", default=False)
  parser.add_argument("-g", "--gui", help="Enable GUI debugging", default=False)
  parser.add_argument("-f", "--filename", help="Input image file", required=True)
  args = parser.parse_args()
  
  is_gui_debugging = args.gui
  logging.basicConfig(filename='out/debug.log',level=logging.DEBUG)
  if args.debug:
    logging.getLogger().addHandler(logging.StreamHandler())

  ocr = VisionAPI()
  detector = ElementDetector()
  detector.ocr = ocr

  if (is_gui_debugging):
    app = QtGui.QApplication(sys.argv)
    gui = ImageDebuggerGUI()
    detector.gui = gui

  print detector.detect(args.filename)

  if (is_gui_debugging):
    gui.show()
    sys.exit(app.exec_())
  