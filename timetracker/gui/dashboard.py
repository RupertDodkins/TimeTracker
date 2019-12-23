""" GUI functionality """

import os
import numpy as np
from datetime import datetime
from PyQt5.QtCore import pyqtSlot, QTimer, QSettings
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QProgressBar, QShortcut
from PyQt5.uic import loadUi
from PyQt5.QtGui import QKeySequence
# import pprint
from timetracker.logs import Logger
from timetracker.data import Data
from timetracker.gui.reports import Reporter
from timetracker.gui.widgets import TodoWidget


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
        TodoWidget(self.todo_groupBox, self.data.daily)
        TodoWidget(self.todo_groupBox_2, self.data.weekly)
        TodoWidget(self.todo_groupBox_3, self.data.monthly)
        self.errandsWidgets()
        self.toolbarWidget()
        self.reportsWidget()

    def frame(self):
        self.conc_mode = False
        title = 'Dashboard'
        self.setWindowTitle(title)
        self.left = 200
        self.top = 100
        self.width = 1360
        self.height = 825
        self.setGeometry(self.left, self.top, self.width, self.height)

    def pomodoroWidget(self):
        self.break_mode = False
        self.pomodoro_duration = 25 * 60  #3
        self.powerhour_duration = 60*60
        self.break_duration = 5 * 60
        self.update_sec = 1
        self.pause_time = self.pomodoro_duration
        self.reset.clicked.connect(self.do_reset)
        self.power.clicked.connect(self.do_longreset)
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

    def errandsWidgets(self):
        for scale in ['daily', 'weekly', 'monthly']:
            comboBox = getattr(self, f'{scale}_comboBox')
            errands = getattr(self.data, scale).errands
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
        self.action_concentration.triggered.connect(self.concentration_mode)
        self.saveshortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.saveshortcut.activated.connect(self.save)
        self.loadshortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.loadshortcut.activated.connect(self.load)
        self.closeshortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.closeshortcut.activated.connect(self.close)
        self.concshortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        self.concshortcut.activated.connect(self.concentration_mode)

    def reportsWidget(self):
        self.reports = Reporter(self)
        self.horizontalLayout_2.addWidget(self.reports)
        self.reports_groupBox.setLayout(self.horizontalLayout_2)
        # self.reports.initialize_lineplots()
        # self.reports.initialize_time_hist()
        # self.reports.update_time_hist()

    def closeEvent(self, event):
        self.logger.gui_save(self.ui, self.settings)
        self.logger.data_save(self.data)
        event.accept()

    def concentration_mode(self):
        self.conc_mode = True
        print('Entering distraction free mode')
        frame_geometry= self.tabWidget.geometry()
        self.tabWidget.setGeometry(frame_geometry.left()-14,frame_geometry.top()-70,self.tabWidget.geometry().width(),
                                   self.tabWidget.geometry().height())
        width = 605
        height = 200
        self.setGeometry(self.left, self.top, width, height)
        self.action_concentration.setText('Enter full display mode')
        self.action_concentration.triggered.disconnect()
        self.action_concentration.triggered.connect(self.full_mode)
        self.concshortcut.activated.disconnect()
        self.concshortcut.activated.connect(self.full_mode)

    def full_mode(self):
        self.conc_mode = False
        print('Entering full display free mode')
        frame_geometry= self.tabWidget.geometry()
        self.tabWidget.setGeometry(frame_geometry.left()+14,frame_geometry.top()+70,self.tabWidget.geometry().width(),
                                   self.tabWidget.geometry().height())
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.action_concentration.setText('Enter concentration mode')
        self.action_concentration.triggered.disconnect()
        self.action_concentration.triggered.connect(self.concentration_mode)
        self.concshortcut.activated.disconnect()
        self.concshortcut.activated.connect(self.concentration_mode)

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
        errand_ind = np.where(text == self.data.daily.errands)[0][0]
        self.prog_errand(errand_ind)
        self.progressBar_3.setValue(self.data.daily.errand_score)

    def weekly_check_errand(self, text):
        errand_ind = np.where(text == self.data.weekly.errands)[0][0]
        self.prog_weekly_errand(errand_ind)
        self.progressBar_4.setValue(self.data.weekly.errand_score)

    def monthly_check_errand(self, text):
        errand_ind = np.where(text == self.data.monthly.errands)[0][0]
        self.prog_weekly_errand(errand_ind)
        self.progressBar_5.setValue(self.data.monthly.errand_score)

    def prog_errand(self, errand_ind):
        progressbar = getattr(self, f"daily_errand_pb_{errand_ind}")

        errand_amount = self.data.daily.errand_amounts[errand_ind]
        errand_complete_yet = self.data.daily.errand_scores[errand_ind] == 100#errand_amount

        if errand_complete_yet:
            self.data.daily.errand_score -= 100./len(self.data.daily.errands)
            self.data.daily.errand_scores[errand_ind] =0#-= 100. / errand_amount
            progressbar.setValue(self.data.daily.errand_scores[errand_ind])
        else:
            self.data.daily.errand_score += 100./(len(self.data.daily.errands)*errand_amount)
            self.data.daily.errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.data.daily.errand_scores[errand_ind])

    def prog_weekly_errand(self, errand_ind):
        progressbar = getattr(self, f"weekly_errand_pb_{errand_ind}")

        errand_amount = self.data.weekly.errand_amounts[errand_ind]
        errand_complete_yet = self.data.weekly.errand_scores[errand_ind] == 100#errand_amount

        if errand_complete_yet:
            self.data.weekly.errand_score -= 100./len(self.data.weekly.errands)
            self.data.weekly.errand_scores[errand_ind] =0#-= 100. / errand_amount
            progressbar.setValue(self.data.weekly.errand_scores[errand_ind])
        else:
            self.data.weekly.errand_score += 100./(len(self.data.weekly.errands)*errand_amount)
            self.data.weekly.errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.data.weekly.errand_scores[errand_ind])

    def prog_time(self):
        self.progressBar_2.setValue(self.data.work_time/self.data.goal_time * 100)

    def disp_time(self):
        self.label_4.setText('%d' % (self.data.work_time/60))

    def update_work_time_times(self):
        now = datetime.now()
        hour = now.hour+float(now.minute)/60.
        self.data.work_time_hours = np.append(self.data.work_time_hours, hour)
        self.data.metrics_history[0] = np.append(self.data.metrics_history[0], self.data.work_time)
        self.data.metrics_history[1] = np.append(self.data.metrics_history[1], self.data.daily.todo_score)
        self.data.metrics_history[2] = np.append(self.data.metrics_history[2],
                                                 (self.data.daily.todo_score/self.data.daily.todo_goal - self.data.work_time/self.data.goal_time)*100)
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
    def do_longreset(self):
        self.timestamp_start = datetime.now()
        self.time = self.powerhour_duration
        self.pause_time = self.powerhour_duration
        self.break_mode = False
        self.display()

    @Qt.pyqtSlot()
    def do_break(self):
        self.timestamp_start = datetime.now()
        self.time = self.break_duration
        self.pause_time = self.break_duration
        self.break_mode = True
        self.display()


