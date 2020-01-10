""" GUI functionality """
# todo integrate with google docs. Look how that pydashboard repo in bookmarks did it. Import that?
# todo quantify impact

import os
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QShortcut
from PyQt5.uic import loadUi
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QSettings
from timetracker.logs import Logger
from timetracker.data import Data
from timetracker.gui.reports import ReportWidget
from timetracker.gui.widgets import TodoWidget, TimerWidget, ErrandWidget

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
        self.timer = TimerWidget(self)
        #todo neaten this up by making args to TodoWidget and Errandwidget match
        todo_groupboxes = [self.todo_groupBox, self.todo_groupBox_2, self.todo_groupBox_3]
        errand_groupboxes = [self.daily_errands_groupBox, self.weekly_errands_groupBox, self.monthly_errands_groupBox]
        timescale_data = [self.data.daily, self.data.weekly,self.data.monthly]
        scales = ['daily', 'weekly', 'monthly']
        self.errandwidgets, self.todowidgets = [], []
        for todo_groupbox, errand_groupbox, timescale_data, scale in zip(todo_groupboxes, errand_groupboxes,
                                                                         timescale_data, scales):
            self.todowidgets.append(TodoWidget(todo_groupbox, timescale_data))
            self.errandwidgets.append(ErrandWidget(self, scale))
        self.toolbarWidget()
        self.reports = ReportWidget(self)

    def frame(self):
        self.conc_mode = False
        title = 'Dashboard'
        self.setWindowTitle(title)
        self.left = 200
        self.top = 100
        self.width = 1360
        self.height = 825
        self.setGeometry(self.left, self.top, self.width, self.height)

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

    def closeEvent(self, event):
        self.logger.gui_save(self.ui, self.settings)
        self.logger.data_save(self.data)
        event.accept()

    def save(self):
        self.logger.gui_save(self.ui, self.settings)
        self.logger.data_save(self.data)

    def load(self):
        self.logger.data_load()
