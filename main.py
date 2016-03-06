import sys
from PyQt4 import QtGui
from gui import ImageDebuggerGUI
from processor import ElementDetector

if __name__ == "__main__":
  # app = QtGui.QApplication(sys.argv)
  # ui = ImageDebuggerGUI()
  # ui.show()
  # sys.exit(app.exec_())
  detector = ElementDetector()
  detector.detect("img/test10.jpg")