"""GUI functionality"""

import os
import numpy as np
from datetime import datetime
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QProgressBar, QCheckBox, QTextEdit, QLineEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.uic import loadUi
# from PyQt5 import QtGui
from PyQt5.QtCore import QSettings
import pprint
from timetracker.logs import Logger
from timetracker.data import Data
from timetracker.gui.reports import Reporter

TICK_TIME = 2**6  #/100

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = loadUi(os.path.dirname(os.path.realpath(__file__))+"/gui.ui", self)

        self.logger = Logger()

        self.settings = QSettings(self.logger.config['gui_cache_address'], QSettings.IniFormat)
        # self.settings = QSettings('settings.ini', QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)    # File only, no fallback to registry or.

        # First get the report type data
        self.data = Data()  # get the defaults
        self.data = self.logger.load_existing_data(self.data)
        # pprint.pprint(self.data.__dict__)

        self.initialize_gui()

        # if gui cache exists it will be loaded and overwrite the defaults
        self.logger.gui_restore(self.ui, self.settings)
        # self.data = self.logger.update_data(self.ui)

    def initialize_gui(self):
        self.frame()
        self.pomodoroWidget()
        self.todoWidget()
        self.errandsWidgets()
        self.toolbarWidget()
        self.reportsWidget()

    def frame(self):
        title = 'Dashboard'
        self.setWindowTitle(title)

        left = 200
        top = 100
        width = 1255
        height = 825
        self.setGeometry(left, top, width, height)

    def pomodoroWidget(self):
        self.break_mode = False
        self.pomodoro_duration = 25 * 60  #3
        self.break_duration = 5 * 60
        self.update_sec = 1
        self.pause_time = self.pomodoro_duration
        self.reset.clicked.connect(self.do_reset)
        self.start.clicked.connect(self.do_start)
        self.break_2.clicked.connect(self.do_break)
        self.timer = QTimer()
        # self.timer.setInterval(1000)
        self.timer.setInterval(TICK_TIME)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.tick)
        self.do_reset()
        self.spinBox.valueChanged.connect(self.update_goaltime)
        self.label_8.setText(str(self.data.pomodoros))
        self.disp_time()

    def todoWidget(self):

        self.last_ind = 0
        self.todo_points = np.zeros((1))
        self.vbox = QVBoxLayout()

        self.todo_checkBoxs = [QCheckBox()]
        self.todo_textEdits = [QTextEdit()]
        self.todo_lineEdits = [QLineEdit()]
        self.todo_pushButtons = [QPushButton()]

        self.todo_checkBoxs[0].setMinimumSize(20,20)
        self.todo_checkBoxs[0].setMaximumSize(20,20)
        self.todo_textEdits[0].setMinimumWidth(400)
        self.todo_textEdits[0].setMaximumWidth(400)
        self.todo_lineEdits[0].setMinimumWidth(41)
        self.todo_lineEdits[0].setMaximumWidth(41)
        self.todo_lineEdits[0].setText(f'{20}')
        self.todo_pushButtons[0].setMinimumWidth(46)
        self.todo_pushButtons[0].setMaximumWidth(46)

        self.todo_pushButtons[0].setText('+')

        self.todo_hBoxs = [QHBoxLayout()]
        self.todo_hBoxs[0].addWidget(self.todo_checkBoxs[0])
        self.todo_hBoxs[0].addWidget(self.todo_textEdits[0])
        self.todo_hBoxs[0].addWidget(self.todo_lineEdits[0])
        self.todo_hBoxs[0].addWidget(self.todo_pushButtons[0])

        self.todo_checkBoxs[0].stateChanged.connect(self.clickBox_wrapper(0))
        self.todo_textEdits[0].textChanged.connect(self.update_todo_text)
        self.todo_lineEdits[0].textChanged.connect(self.score_changed_wrapper(0))
        self.todo_pushButtons[0].clicked.connect(self.add_todo)

        self.vbox.addLayout(self.todo_hBoxs[0] )
        self.vbox.addWidget(self.progressBar)
        self.todo_groupBox.setLayout(self.vbox)


    def add_todo(self):
        this_ind = len(self.todo_hBoxs)
        self.todo_points = np.append(self.todo_points,0)

        self.todo_checkBoxs = np.append(self.todo_checkBoxs, QCheckBox())
        self.todo_checkBoxs[this_ind].stateChanged.connect(self.clickBox_wrapper(this_ind))
        self.todo_checkBoxs[this_ind].setMinimumSize(20,20)
        self.todo_checkBoxs[this_ind].setMaximumSize(20,20)

        self.todo_textEdits = np.append(self.todo_textEdits, QTextEdit())
        self.todo_textEdits[this_ind].textChanged.connect(self.update_todo_text)
        self.todo_textEdits[this_ind].setMinimumWidth(400)
        self.todo_textEdits[this_ind].setMaximumWidth(400)

        self.todo_lineEdits = np.append(self.todo_lineEdits, QLineEdit())
        self.todo_lineEdits[this_ind].textChanged.connect(self.score_changed_wrapper(this_ind))
        self.todo_lineEdits[this_ind].setMinimumWidth(41)
        self.todo_lineEdits[this_ind].setMaximumWidth(41)
        self.todo_lineEdits[this_ind].setText(f'{20}')

        self.todo_pushButtons = np.append(self.todo_pushButtons, QPushButton())
        self.todo_pushButtons[this_ind].setMinimumWidth(46)
        self.todo_pushButtons[this_ind].setMaximumWidth(46)
        self.todo_pushButtons[this_ind].setText('x')

        self.todo_hBoxs = np.append(self.todo_hBoxs, QHBoxLayout())
        self.todo_hBoxs[this_ind].addWidget(self.todo_checkBoxs[this_ind])
        self.todo_hBoxs[this_ind].addWidget(self.todo_textEdits[this_ind])
        self.todo_hBoxs[this_ind].addWidget(self.todo_lineEdits[this_ind])
        self.todo_hBoxs[this_ind].addWidget(self.todo_pushButtons[this_ind])

        self.todo_pushButtons[this_ind].clicked.connect(self.remove_todo_wrapper(this_ind))

        self.vbox.addLayout(self.todo_hBoxs[this_ind])

        self.progressBar.setParent(None)
        self.progressBar = QProgressBar()
        self.progressBar.setValue(100*self.data.todo_score/self.data.todo_goal)
        self.progressBar.setGeometry(0,215,585,30)
        self.progressBar.setMinimumSize(585,30)
        self.progressBar.setMaximumSize(585,30)
        self.vbox.addWidget(self.progressBar)
        self.todo_groupBox.setLayout(self.vbox)

    def remove_todo_wrapper(self, this_ind):
        def remove_todo():
            # remove the hbox contents
            self.todo_checkBoxs[this_ind].setParent(None)
            self.todo_textEdits[this_ind].setParent(None)
            self.todo_lineEdits[this_ind].setParent(None)
            self.todo_pushButtons[this_ind].setParent(None)

            # delete the element from each list including the hox (row)
            self.todo_checkBoxs = np.delete(self.todo_checkBoxs, this_ind)
            self.todo_textEdits = np.delete(self.todo_textEdits, this_ind)
            self.todo_lineEdits = np.delete(self.todo_lineEdits, this_ind)
            self.todo_pushButtons = np.delete(self.todo_pushButtons, this_ind)
            self.todo_hBoxs = np.delete(self.todo_hBoxs, this_ind)

            self.todo_points = np.delete(self.todo_points, this_ind)

            # recalculate everything
            for ind in range(1,self.last_ind):
                self.todo_pushButtons[ind].clicked.disconnect()
                self.todo_pushButtons[ind].clicked.connect(self.remove_todo_wrapper(ind))
                self.todo_checkBoxs[ind].stateChanged.disconnect()
                self.todo_checkBoxs[ind].stateChanged.connect(self.clickBox_wrapper(ind))
                self.todo_lineEdits[ind].textChanged.disconnect()
                self.todo_lineEdits[ind].textChanged.connect(self.score_changed_wrapper(ind))
            self.last_ind = len(self.todo_hBoxs) - 1  # first row is 0
            self.data.todo_score = np.sum(self.todo_points)
            self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
            self.update_todo_text()
            self.progressBar.setValue(100 * self.data.todo_score / self.data.todo_goal)

        return remove_todo

    def score_changed_wrapper(self, this_ind):
        def on_score_changed():
            if self.todo_checkBoxs[this_ind].isChecked():
                self.todo_points[this_ind] = self.todo_lineEdits[this_ind].text()
            self.data.todo_score = np.sum(self.todo_points)
            try:
                self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
            except ValueError:
                pass
        return on_score_changed

    def clickBox_wrapper(self, this_ind):
        def clickBox(state):
            if state == QtCore.Qt.Checked:
                self.add_points(this_ind)
            else:
                self.sub_points(this_ind)
        return clickBox

    def add_points(self, this_ind):
        self.todo_points[this_ind] = int(self.todo_lineEdits[this_ind].text())
        self.data.todo_score = np.sum(self.todo_points)
        self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
        self.progressBar.setValue(100*self.data.todo_score/self.data.todo_goal)

    def sub_points(self, this_ind):
        self.todo_points[this_ind] = 0
        self.data.todo_score = np.sum(self.todo_points)
        self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
        self.progressBar.setValue(100*self.data.todo_score/self.data.todo_goal)

    def errandsWidgets(self):
        for scale in ['daily', 'weekly']:
            comboBox = getattr(self, f'{scale}_comboBox')
            errands = getattr(self.data, f'{scale}_errands')
            errands_groupBox = getattr(self, f'{scale}_errands_groupBox')
            comboBox.addItems(str(errand) for errand in errands)
            # num_errands = len(self.data.daily_errands)
            # num_rows = num_errands//3
            # comboBox_row = num_rows if num_errands % 3 != 0 else num_rows+1
            comboBox.setGeometry(390, 125, 200, 31)
            comboBox.activated[str].connect(getattr(self, f'{scale}_check_errand'))
            for i in range(len(errands)):
                row = i //3
                col = i % 3

                setattr(self, f'{scale}_errands_label_{i}', QLabel(errands_groupBox))
                setattr(self, f'{scale}_errand_pb_{i}', QProgressBar(errands_groupBox))

                errands_QLabel = getattr(self, f"{scale}_errands_label_{i}")
                errands_QLabel.setText(str(errands[i]))
                errands_QLabel.setGeometry(col*200 + 10, row*30 + 30,90,16)

                errands_QProgressBar = getattr(self, f"{scale}_errand_pb_{i}")
                errands_QProgressBar.setGeometry(col*200 + 110, row*30 + 30,71,20)
                errands_QProgressBar.setValue(0)

    def toolbarWidget(self):
        self.actionSave_2.triggered.connect(self.save)
        self.actionLoad_2.triggered.connect(self.load)
        self.actionClose.triggered.connect(self.close)

    def reportsWidget(self):
        self.reports = Reporter(self)
        self.horizontalLayout_2.addWidget(self.reports)
        self.reports_groupBox.setLayout(self.horizontalLayout_2)
        # self.reports.initialize_lineplots()
        # self.reports.initialize_time_hist()
        # self.reports.update_time_hist()

    def update_todo_text(self):
        self.data.todos = [textEdit.toPlainText() for textEdit in self.todo_textEdits]

    def closeEvent(self, event):
        self.logger.gui_save(self.ui, self.settings)
        self.logger.data_save(self.data)
        event.accept()

    def save(self):
        self.logger.gui_save(self.ui, self.settings)
        self.logger.data_save(self.data)

    def load(self):
        self.logger.data_load()

    def update_pomodoros(self):
        self.data.pomodoros += 1
        self.label_8.setText(str(self.data.pomodoros))

    def update_goaltime(self):
        self.data.goal_time = self.spinBox.value() * 25 * 60
        self.reports.update_goals(self.data.goals)

    def daily_check_errand(self, text):
        errand_ind = np.where(text == self.data.daily_errands)[0][0]
        self.prog_errand(errand_ind)
        self.progressBar_3.setValue(self.data.daily_errand_score)

    def weekly_check_errand(self, text):
        errand_ind = np.where(text == self.data.weekly_errands)[0][0]
        self.prog_weekly_errand(errand_ind)
        self.progressBar_4.setValue(self.data.weekly_errand_score)

    def prog_errand(self, errand_ind):
        progressbar = getattr(self, f"daily_errand_pb_{errand_ind}")

        errand_amount = self.data.daily_errand_amounts[errand_ind]
        errand_complete_yet = self.data.daily_errand_scores[errand_ind] == 100#errand_amount

        if errand_complete_yet:
            self.data.daily_errand_score -= 100./len(self.data.daily_errands)
            self.data.daily_errand_scores[errand_ind] =0#-= 100. / errand_amount
            progressbar.setValue(self.data.daily_errand_scores[errand_ind])
        else:
            self.data.daily_errand_score += 100./(len(self.data.daily_errands)*errand_amount)
            self.data.daily_errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.data.daily_errand_scores[errand_ind])

    def prog_weekly_errand(self, errand_ind):
        progressbar = getattr(self, f"weekly_errand_pb_{errand_ind}")

        errand_amount = self.data.weekly_errand_amounts[errand_ind]
        errand_complete_yet = self.data.weekly_errand_scores[errand_ind] == 100#errand_amount

        if errand_complete_yet:
            self.data.weekly_errand_score -= 100./len(self.data.weekly_errands)
            self.data.weekly_errand_scores[errand_ind] =0#-= 100. / errand_amount
            progressbar.setValue(self.data.weekly_errand_scores[errand_ind])
        else:
            self.data.weekly_errand_score += 100./(len(self.data.weekly_errands)*errand_amount)
            self.data.weekly_errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.data.weekly_errand_scores[errand_ind])

    def prog_time(self):
        self.progressBar_2.setValue(self.data.work_time/self.data.goal_time * 100)

    def disp_time(self):
        self.label_4.setText('%d' % (self.data.work_time/60))

    def update_work_time_times(self):
        now = datetime.now()
        hour = now.hour+float(now.minute)/60.
        self.data.work_time_hours = np.append(self.data.work_time_hours, hour)
        # self.data.work_time_history = np.append(self.data.work_time_history, self.data.work_time)
        self.data.metrics_history[0] = np.append(self.data.metrics_history[0], self.data.work_time)
        self.data.metrics_history[1] = np.append(self.data.metrics_history[1], self.data.todo_score)
        self.data.metrics_history[2] = np.append(self.data.metrics_history[2],
                                                 (self.data.todo_score/self.data.todo_goal - self.data.work_time/self.data.goal_time)*100)
        self.reports.update_lineplots()
        # self.reports.update_time_hist()

    def keyPressEvent(self, event):
        if event.key() == Qt.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def display(self):
        if self.time < 0:
            self.lcd.setDigitCount(6)
            self.lcd.display("-%d:%.2d" % (abs(self.time) // 60, abs(self.time) % 60))
        else:
            self.lcd.setDigitCount(5)
            self.lcd.display("%d:%.2d" % (self.time // 60, self.time % 60))

    @Qt.pyqtSlot()
    def tick(self):
        orig_time = self.time

        self.time -= TICK_TIME / 1000

        delta = datetime.now() - self.timestamp_start
        delta = delta.total_seconds()
        if self.break_mode:
            if np.int(self.time) != self.break_duration - np.int(delta):
                self.time = self.pause_time - np.int(delta)
        else:
            self.data.work_time += TICK_TIME / 1000
            self.prog_time()
            self.disp_time()

            if np.int(self.time) != self.pomodoro_duration - np.int(delta):
                difference = self.time - (self.pause_time - np.int(delta))
                self.data.work_time += difference
                self.time = self.pause_time - np.int(delta)

            #todo update to do it on every pmodoro_time interval
            #something like orig_time % self.pomodoro_time >= 0 and self.time % self.pomodoro_time < 0
            if orig_time >= 0 and self.time < 0:  # timer transitions below 0
                self.update_pomodoros()

            if orig_time//self.update_sec != self.time//self.update_sec:  # timer transitions past minute mark
                self.update_work_time_times()

        self.display()

    @Qt.pyqtSlot()
    def do_start(self):
        self.timestamp_start = datetime.now()
        self.timer.start()
        self.start.setText("Pause")
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.do_pause)

    @Qt.pyqtSlot()
    def do_pause(self):
        self.pause_time = self.time
        self.timer.stop()
        self.start.setText("Start")
        self.start.clicked.disconnect()
        self.start.clicked.connect(self.do_start)

    @Qt.pyqtSlot()
    def do_reset(self):
        self.timestamp_start = datetime.now()
        self.time = self.pomodoro_duration
        self.pause_time = self.pomodoro_duration
        self.break_mode = False
        self.display()

    @Qt.pyqtSlot()
    def do_break(self):
        self.timestamp_start = datetime.now()
        self.time = self.break_duration
        self.pause_time = self.break_duration
        self.break_mode = True
        self.display()

