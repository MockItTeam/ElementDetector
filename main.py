import sys
from PyQt4 import QtGui
from gui import ImageDebuggerGUI

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  ui = ImageDebuggerGUI()
  ui.show()
  sys.exit(app.exec_())