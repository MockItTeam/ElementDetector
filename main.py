import sys
import logging
import argparse
import json
import traceback

# from gui import ImageDebuggerGUI
from processor import ElementDetector
from step import FileWriterStepDebugger, StepDebugger
from timeout import timeout

@timeout(60)
def init_processor():
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--debug", help="Enable console debugging", default=False)
  # parser.add_argument("-g", "--gui", help="Enable GUI debugging", default=False)
  parser.add_argument("-f", "--filename", help="Input image file", required=True)
  parser.add_argument("-o", "--ocr", help="Enable OCR", default=False)
  parser.add_argument("-s", "--step", help="Enable full step debugging", default=False)
  args = parser.parse_args()
  
  # is_gui_debugging = args.gui
  debug_output = "/tmp/mockit-processor.log"
  open(debug_output, "w+")
  logging.basicConfig(filename=debug_output ,level=logging.DEBUG)
  
  if args.debug:
    logging.getLogger().addHandler(logging.StreamHandler())

  detector = ElementDetector()
  
  if (args.step):
    step = FileWriterStepDebugger()
  else:
    step = StepDebugger()

  detector.step = step

  if (args.ocr):
    from google import VisionAPI
    ocr = VisionAPI()
    detector.ocr = ocr

  # if (is_gui_debugging):
    # from PyQt4 import QtGui
    # app = QtGui.QApplication(sys.argv)
    # gui = ImageDebuggerGUI()
    # detector.gui = gui

  print detector.detect(args.filename)

  # if (is_gui_debugging):
    # gui.show()
    # sys.exit(app.exec_())
  
if __name__ == "__main__":
  try:
    init_processor()
  except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error_message = ''.join(line for line in lines)
    print '{"error_message":' + json.dumps(error_message) + '}'