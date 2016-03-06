import sys
from PyQt4 import QtCore, QtGui

class sliderdemo(QtGui.QWidget):
   def __init__(self, parent = None):
      super(sliderdemo, self).__init__(parent)

      layout = QtGui.QVBoxLayout()
      self.l1 = QtGui.QLabel("Hello")
      self.l1.setAlignment(QtCore.Qt.AlignCenter)
      layout.addWidget(self.l1)
    
      self.sl = QtGui.QSlider(QtCore.Qt.Horizontal)
      self.sl.setMinimum(10)
      self.sl.setMaximum(100)
      self.sl.setValue(20)
      self.sl.setTickPosition(QtGui.QSlider.TicksBelow)
      self.sl.setTickInterval(10)
    
      layout.addWidget(self.sl)
      self.sl.valueChanged.connect(self.valuechange)
      self.setLayout(layout)
      self.setWindowTitle("SpinBox demo")

      self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

   def valuechange(self):
      size = self.sl.value()
      # self.l1.setFont(QFont("Arial",size))
      self.l1.setText(str(size));
    
def main():
   app = QtGui.QApplication(sys.argv)
   ex = sliderdemo()
   # ex.setWindowState(ex.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
   # ex.activateWindow()
   ex.show()
   sys.exit(app.exec_())
  
if __name__ == '__main__':
   main()