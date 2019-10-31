"""GUI functionality"""

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

TICK_TIME = 2**6

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("Dashboard/gui.ui", self)

        self.todo_score = 0
        self.work_time = 0.
        self.goal_time = 4*60*60

        title = 'Dashboard'
        left = 500
        top = 100
        width = 650
        height = 775
        self.setWindowTitle(title)
        self.setGeometry(left, top, width, height)

        self.reset.clicked.connect(self.do_reset)
        self.start.clicked.connect(self.do_start)

        self.timer = QTimer()
        self.timer.setInterval(TICK_TIME)
        self.timer.timeout.connect(self.tick)

        self.do_reset()

        for checkboxes in [self.checkBox, self.checkBox_2, self.checkBox_3]:
            checkboxes.stateChanged.connect(self.clickBox)

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            print('Checked')
            self.add_prog()
        else:
            print('Unchecked')
            self.sub_prog()

    def add_prog(self):
        self.todo_score += 100./3
        self.progressBar.setValue(self.score)

    def sub_prog(self):
        self.todo_score -= 100./3
        self.progressBar.setValue(self.score)

    def prog_time(self):
        self.progressBar_2.setValue(self.work_time/self.goal_time * 100)

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

        self.work_time += TICK_TIME / 1000
        self.prog_time()

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
