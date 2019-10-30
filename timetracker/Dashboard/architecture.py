"""GUI architecture goes here"""

from PyQt5.QtCore import pyqtSlot, QTimer, QTime
from PyQt5 import Qt
from PyQt5.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QWidget, QPushButton, \
    QProgressBar, QRadioButton, QSlider, QLabel, QMainWindow
from PyQt5.uic import loadUi
# from gui import Ui_MainWindow

TICK_TIME = 2**6

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("Dashboard/gui.ui", self)

        title = 'Daily Dashboard'
        left = 10
        top = 10
        width = 800
        height = 1250
        self.setWindowTitle(title)
        self.setGeometry(left, top, width, height)

        self.reset.clicked.connect(self.do_reset)
        self.start.clicked.connect(self.do_start)

        self.timer = QTimer()
        self.timer.setInterval(TICK_TIME)
        self.timer.timeout.connect(self.tick)

        self.do_reset()

    def keyPressEvent(self, event):
        if event.key() == Qt.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def display(self):
        self.lcd.display("%d:%05.2f" % (self.time // 60, self.time % 60))

    @Qt.pyqtSlot()
    def tick(self):
        self.time -= TICK_TIME / 1000
        self.display()

    @Qt.pyqtSlot()
    def do_start(self):
        self.timer.start()
        self.start.setText("Pause")
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.do_pause)

    @Qt.pyqtSlot()
    def do_pause(self):
        self.timer.stop()
        self.start.setText("Start")
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.do_start)

    @Qt.pyqtSlot()
    def do_reset(self):
        self.time = 25
        self.display()

    @pyqtSlot()
    def In_clicked(self):
        print('not implemented')

    @pyqtSlot()
    def Out_clicked(self):
        print('not implemented')

    # def showTime(self):
    #     time = QTime.currentTime()
    #     text = time.toString('hh:mm')
    #     self.display(text)