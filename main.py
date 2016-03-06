import sys
from PyQt4 import QtGui
from gui import ImageDebuggerGUI
from processor import ElementDetector

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  gui = ImageDebuggerGUI()
  detector = ElementDetector(gui)
  detector.detect("img/test10.jpg")
  gui.show()
  sys.exit(app.exec_())