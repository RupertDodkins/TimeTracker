"""GUI functionality"""

import numpy as np
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtGui
from PyQt5.QtCore import QSettings
from timetracker.logs import Logger
from timetracker.data import Data

TICK_TIME = 2**6  #/100

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = loadUi("Dashboard/gui.ui", self)

        self.logger = Logger()

        GUI_cache_exists = self.logger.check_today()
        print(GUI_cache_exists)
        if GUI_cache_exists:
            self.data = self.load()
        else:
            self.data = Data()
        print(self.data.errand_score, self.data.errand_scores, self.data.todos)

        self.settings = QSettings('settings.ini', QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)    # File only, no fallback to registry or or.

        title = 'Dashboard'
        left = 200
        top = 100
        width = 1255
        height = 790
        self.setWindowTitle(title)
        self.setGeometry(left, top, width, height)
        # self.resize(self.settings.value('size', QtCore.QSize(270, 225)))
        # self.move(self.settings.value('pos', QtCore.QPoint(50, 50)))

        self.break_mode = False
        self.reset.clicked.connect(self.do_reset)
        self.start.clicked.connect(self.do_start)
        self.break_2.clicked.connect(self.do_break)
        self.timer = QTimer()
        self.timer.setInterval(TICK_TIME)
        self.timer.timeout.connect(self.tick)
        self.do_reset()

        self.spinBox.valueChanged.connect(self.update_goaltime)

        for checkboxes in [self.checkBox_1, self.checkBox_2, self.checkBox_3]:
            checkboxes.stateChanged.connect(self.clickBox)

        self.comboBox.addItems(errand for errand in self.data.errands)
        self.comboBox.activated[str].connect(self.check_errand)

        self.actionSave_2.triggered.connect(self.save)
        self.actionLoad_2.triggered.connect(self.load)
        self.actionClose.triggered.connect(self.close)

        # self.progressBar_3.setValue(int(self.settings.value('prog3', 50)))
        self.logger.GuiRestore(self.ui, self.settings)

    def closeEvent(self, event):
        self.logger.GuiSave(self.ui, self.settings)
        event.accept()

        # messagebox = QMessageBox(QMessageBox.Question, "Title text", "Do you want to save?", buttons = QMessageBox.Discard | QMessageBox.Cancel | QMessageBox.Ok, parent=self)
        # messagebox.setDefaultButton(QMessageBox.Ok)
        # reply = messagebox.exec_()
        # if reply == QMessageBox.Ok:
        #     self.save()
        #     event.accept()
        # elif reply == QMessageBox.Discard:
        #     event.accept()
        # else:
        #     event.ignore()

    def save(self):
        # self.logger.save_today(self.data)
        # settings = QtCore.QSettings('my_org', 'my_app')
        # self.logger.save_today(self.ui, settings)
        print('sol')

    def load(self):
        print('lol')
        # self.data = self.logger.load_today()
        # self.label_8.setText(str(self.data.pomodoros))
        # settings = QtCore.QSettings('my_org', 'my_app')
        # self.logger.load_today(self.ui, settings)

    def update_pomodoros(self):
        self.data.pomodoros += 1
        self.label_8.setText(str(self.data.pomodoros))

    def update_goaltime(self):
        self.data.goal_time = self.spinBox.value() * 25 * 60

    def check_errand(self, text):
        errand_ind = np.where(text == self.data.errands)[0][0]
        self.prog_errand(errand_ind)
        self.progressBar_3.setValue(self.data.errand_score)

    def prog_errand(self, errand_ind):
        progressbar = getattr(self, f"errand_progressBar_{errand_ind}")

        errand_amount = self.data.errand_amounts[errand_ind]
        errand_complete_yet = self.data.errand_scores[errand_ind] == 100#errand_amount

        if errand_complete_yet:
            self.data.errand_score -= 100./len(self.data.errands)
            self.data.errand_scores[errand_ind] =0#-= 100. / errand_amount
            progressbar.setValue(self.data.errand_scores[errand_ind])
        else:
            self.data.errand_score += 100./(len(self.data.errands)*errand_amount)
            self.data.errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.data.errand_scores[errand_ind])

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.add_prog()
        else:
            self.sub_prog()

    def add_prog(self):
        self.data.todo_score += 100./3
        self.progressBar.setValue(self.data.todo_score)

    def sub_prog(self):
        self.data.todo_score -= 100./3
        self.progressBar.setValue(self.data.todo_score)

    def prog_time(self):
        self.progressBar_2.setValue(self.data.work_time/self.data.goal_time * 100)

    def disp_time(self):
        self.label_4.setText('%d' % (self.data.work_time/60))

    def keyPressEvent(self, event):
        if event.key() == Qt.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def display(self):
        if self.time < 0:
            self.lcd.setDigitCount(6)
        else:
            self.lcd.setDigitCount(5)
        # self.lcd.display("%d:%.2f" % (self.time // 60, self.time % 60))
        self.lcd.display("%d:%.2d" % (self.time // 60, self.time % 60))


    @Qt.pyqtSlot()
    def tick(self):

        if self.time > 0 and self.time - TICK_TIME / 1000 <0:
            self.update_pomodoros()

        self.time -= TICK_TIME / 1000
        self.display()

        if not self.break_mode:
            self.data.work_time += TICK_TIME / 1000
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

