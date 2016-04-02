import sys
import logging
import argparse

from gui import ImageDebuggerGUI
from processor import ElementDetector


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--debug", help="Enable console debugging", default=False)
  parser.add_argument("-g", "--gui", help="Enable GUI debugging", default=False)
  parser.add_argument("-f", "--filename", help="Input image file", required=True)
  parser.add_argument("-o", "--ocr", help="Enable OCR", default=False)
  args = parser.parse_args()
  
  is_gui_debugging = args.gui
  logging.basicConfig(filename='out/debug.log',level=logging.DEBUG)
  if args.debug:
    logging.getLogger().addHandler(logging.StreamHandler())

  detector = ElementDetector()
  
  if (args.ocr):
    from google import VisionAPI
    ocr = VisionAPI()
    detector.ocr = ocr

  if (is_gui_debugging):
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    gui = ImageDebuggerGUI()
    detector.gui = gui

  print detector.detect(args.filename)

  if (is_gui_debugging):
    gui.show()
    sys.exit(app.exec_())
  