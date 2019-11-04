"""GUI functionality"""

import numpy as np
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

TICK_TIME = 2**6

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("Dashboard/gui.ui", self)

        self.errands = np.array(['Drink 3 bottles', 'Read paper', 'Get result for Ben', 'Meditate', 'NN',
                                 'Update YNAB'])
        self.errand_amounts = np.array([3., 1, 1, 1, 1, 1])
        self.errand_scores = np.zeros_like((self.errand_amounts))

        self.todo_score = 0
        self.work_time = 0.
        self.goal_time = 4*60*60
        self.errand_score = 0
        self.break_mode = False

        title = 'Dashboard'
        left = 500
        top = 100
        width = 640
        height = 900
        self.setWindowTitle(title)
        self.setGeometry(left, top, width, height)

        self.reset.clicked.connect(self.do_reset)
        self.start.clicked.connect(self.do_start)
        self.break_2.clicked.connect(self.do_break)

        self.timer = QTimer()
        self.timer.setInterval(TICK_TIME)
        self.timer.timeout.connect(self.tick)

        self.do_reset()

        for checkboxes in [self.checkBox_1, self.checkBox_2, self.checkBox_3]:
            checkboxes.stateChanged.connect(self.clickBox)

        self.comboBox.addItems(errand for errand in self.errands)
        self.comboBox.activated[str].connect(self.check_errand)

    def check_errand(self, text):
        errand_ind = np.where(text == self.errands)[0][0]
        self.prog_errand(errand_ind)
        self.progressBar_3.setValue(self.errand_score)

    def prog_errand(self, errand_ind):
        progressbar = getattr(self, f"errand_progressBar_{errand_ind}")

        errand_amount = self.errand_amounts[errand_ind]
        errand_complete_yet = self.errand_scores[errand_ind] == 100#errand_amount
        print(errand_ind, progressbar.value(), errand_complete_yet, self.errand_scores[errand_ind], 'here', 100. / errand_amount)

        if errand_complete_yet:
            self.errand_score -= 100./len(self.errands)
            self.errand_scores[errand_ind] =0#-= 100. / errand_amount
            progressbar.setValue(self.errand_scores[errand_ind])
        else:
            self.errand_score += 100./(len(self.errands)*errand_amount)
            self.errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.errand_scores[errand_ind])
        print(errand_ind, progressbar.value(), errand_complete_yet, self.errand_scores[errand_ind], 'here',
              100. / errand_amount)
        # print(progressbar.value(), 100./errand_amount)

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.add_prog()
        else:
            self.sub_prog()

    def add_prog(self):
        self.todo_score += 100./3
        self.progressBar.setValue(self.todo_score)

    def sub_prog(self):
        self.todo_score -= 100./3
        self.progressBar.setValue(self.todo_score)

    def prog_time(self):
        self.progressBar_2.setValue(self.work_time/self.goal_time * 100)

    def disp_time(self):
        self.label_4.setText('%d' % (self.work_time/60))

    def keyPressEvent(self, event):
        if event.key() == Qt.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def display(self):
        # self.lcd.display("%d:%.2f" % (self.time // 60, self.time % 60))
        self.lcd.display("%d:%.2d" % (self.time // 60, self.time % 60))

    @Qt.pyqtSlot()
    def tick(self):
        self.time -= TICK_TIME / 1000
        self.display()

        if not self.break_mode:
            self.work_time += TICK_TIME / 1000
            self.prog_time()
            self.disp_time()

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
        self.time = 25*60
        self.break_mode = False
        self.display()

    @Qt.pyqtSlot()
    def do_break(self):
        self.time = 5*60
        self.break_mode = True
        self.display()

