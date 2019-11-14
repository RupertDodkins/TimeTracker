""" Currently all this functionality is part of architecture. Will host the widget for pomodoro stop watch """
import matplotlib.pylab as plt
import numpy as np
from datetime import datetime
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
import time

TICK_TIME = 2**6  #/100

class Timer(QMainWindow):
    """ A class to display the historical data """

    def __init__(self, ui):
        self.ui = ui
        self.break_mode = False
        self.pomodoro_duration = 25 * 60  #3
        self.break_duration = 5 * 60
        self.pause_time = self.pomodoro_duration

        self.timer = QTimer()
        # self.timer.setInterval(1000)
        self.timer.setInterval(TICK_TIME)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.tick)
        self.do_reset()

    def keyPressEvent(self, event):
        if event.key() == Qt.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def display(self):
        if self.time < 0:
            self.ui.lcd.setDigitCount(6)
            self.ui.lcd.display("-%d:%.2d" % (abs(self.time) // 60, abs(self.time) % 60))
        else:
            self.ui.lcd.setDigitCount(5)
            # self.lcd.display("%d:%.2f" % (self.time // 60, self.time % 60))
            self.ui.lcd.display("%d:%.2d" % (self.time // 60, self.time % 60))

    @Qt.pyqtSlot()
    def tick(self):
        print(self.time, TICK_TIME / 1000, self.time - TICK_TIME / 1000, self.time > 0,
              self.time - TICK_TIME / 1000 < 0, self.time > 0 and self.time - TICK_TIME / 1000 < 0)

        orig_time = self.time

        self.time -= TICK_TIME / 1000

        delta = datetime.now() - self.timestamp_start
        delta = delta.total_seconds()
        print(self.time, self.pomodoro_duration - delta, self.data.work_time)
        if self.break_mode:
            if np.int(self.time) != self.break_duration - np.int(delta):
                print('Using delta', delta)
                self.time = self.pause_time - np.int(delta)
        else:
            self.data.work_time += TICK_TIME / 1000
            self.prog_time()
            self.disp_time()

            if np.int(self.time) != self.pomodoro_duration - np.int(delta):
                difference = self.time - (self.pause_time - np.int(delta))
                print('Using delta', delta, difference)
                self.data.work_time += difference
                self.time = self.pause_time - np.int(delta)

            if orig_time >= 0 and self.time < 0:
                self.update_pomodoros()

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

