""" todo write docstring

todo get weekly todos loading each time
 """

import numpy as np
from datetime import datetime
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QProgressBar, QCheckBox, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, \
    QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer

class TodoWidget():
    def __init__(self, groupbox, timescale_data):

        self.groupbox = groupbox
        self.timescale_data = timescale_data

        self.std_worth = 20
        self.last_ind = 0
        self.vbox = QVBoxLayout()

        self.checkBoxs = [QCheckBox()]
        self.textEdits = [QTextEdit()]
        self.lineEdits = [QLineEdit()]
        self.pushButtons = [QPushButton()]

        self.checkBoxs[0].setMinimumSize(20,20)
        self.checkBoxs[0].setMaximumSize(20,20)
        self.textEdits[0].setMinimumWidth(400)
        self.textEdits[0].setMaximumWidth(400)
        self.lineEdits[0].setMinimumWidth(41)
        self.lineEdits[0].setMaximumWidth(41)
        self.lineEdits[0].setText(f'{self.std_worth}')
        self.pushButtons[0].setMinimumWidth(46)
        self.pushButtons[0].setMaximumWidth(46)

        self.pushButtons[0].setText('+')

        self.hBoxs = [QHBoxLayout()]
        self.hBoxs[0].addWidget(self.checkBoxs[0])
        self.hBoxs[0].addWidget(self.textEdits[0])
        self.hBoxs[0].addWidget(self.lineEdits[0])
        self.hBoxs[0].addWidget(self.pushButtons[0])

        self.checkBoxs[0].stateChanged.connect(self.clickBox_wrapper(0))
        self.textEdits[0].textChanged.connect(self.update_text)
        self.lineEdits[0].textChanged.connect(self.score_changed_wrapper(0))
        self.pushButtons[0].clicked.connect(self.add_todo)

        self.vbox.addLayout(self.hBoxs[0])
        self.progressBar = QProgressBar()
        self.progressBar.setValue(100*self.timescale_data.todo_score/self.timescale_data.todo_goal)
        self.progressBar.setGeometry(0,215,585,30)
        self.progressBar.setMinimumSize(585,30)
        self.progressBar.setMaximumSize(585,30)
        self.vbox.addWidget(self.progressBar)
        self.groupbox.setLayout(self.vbox)

        if len(self.timescale_data.todos) >0:
            self.load()

    def load(self):
        points = self.timescale_data.points*1  #store the points
        worths = self.timescale_data.worths*1  #store the points
        [self.add_todo() for _ in range(len(self.timescale_data.todos)-1)]
        [textEdit.setText(todo) for textEdit, todo in zip(self.textEdits, self.timescale_data.todos)]
        self.timescale_data.points = points
        self.timescale_data.worths = worths
        [checkbox.setChecked(True) for checkbox in self.checkBoxs[points!=0]]
        [self.lineEdits[td].setText(str(int(worth))) for td, worth in enumerate(self.timescale_data.worths)]

    def add_todo(self):
        this_ind = len(self.hBoxs)
        self.timescale_data.points = np.append(self.timescale_data.points,0)
        self.timescale_data.worths = np.append(self.timescale_data.worths,self.std_worth)
        print(self.timescale_data.worths)

        self.checkBoxs = np.append(self.checkBoxs, QCheckBox())
        self.checkBoxs[this_ind].stateChanged.connect(self.clickBox_wrapper(this_ind))
        self.checkBoxs[this_ind].setMinimumSize(20,20)
        self.checkBoxs[this_ind].setMaximumSize(20,20)

        self.textEdits = np.append(self.textEdits, QTextEdit())
        self.textEdits[this_ind].textChanged.connect(self.update_text)
        self.textEdits[this_ind].setMinimumWidth(400)
        self.textEdits[this_ind].setMaximumWidth(400)

        self.lineEdits = np.append(self.lineEdits, QLineEdit())
        self.lineEdits[this_ind].textChanged.connect(self.score_changed_wrapper(this_ind))
        self.lineEdits[this_ind].setMinimumWidth(41)
        self.lineEdits[this_ind].setMaximumWidth(41)
        self.lineEdits[this_ind].setText(f'{20}')

        self.pushButtons = np.append(self.pushButtons, QPushButton())
        self.pushButtons[this_ind].setMinimumWidth(46)
        self.pushButtons[this_ind].setMaximumWidth(46)
        self.pushButtons[this_ind].setText('x')

        self.hBoxs = np.append(self.hBoxs, QHBoxLayout())
        self.hBoxs[this_ind].addWidget(self.checkBoxs[this_ind])
        self.hBoxs[this_ind].addWidget(self.textEdits[this_ind])
        self.hBoxs[this_ind].addWidget(self.lineEdits[this_ind])
        self.hBoxs[this_ind].addWidget(self.pushButtons[this_ind])

        self.pushButtons[this_ind].clicked.connect(self.remove_wrapper(this_ind))

        self.vbox.addLayout(self.hBoxs[this_ind])

        self.progressBar.setParent(None)
        self.progressBar = QProgressBar()
        self.progressBar.setValue(100*self.timescale_data.todo_score/self.timescale_data.todo_goal)
        self.progressBar.setGeometry(0,215,585,30)
        self.progressBar.setMinimumSize(585,30)
        self.progressBar.setMaximumSize(585,30)
        self.vbox.addWidget(self.progressBar)
        self.groupbox.setLayout(self.vbox)

    def remove_wrapper(self, this_ind):
        def remove_todo():
            # remove the hbox contents
            self.checkBoxs[this_ind].setParent(None)
            self.textEdits[this_ind].setParent(None)
            self.lineEdits[this_ind].setParent(None)
            self.pushButtons[this_ind].setParent(None)

            # delete the element from each list including the hox (row)
            self.checkBoxs = np.delete(self.checkBoxs, this_ind)
            self.textEdits = np.delete(self.textEdits, this_ind)
            self.lineEdits = np.delete(self.lineEdits, this_ind)
            self.pushButtons = np.delete(self.pushButtons, this_ind)
            self.hBoxs = np.delete(self.hBoxs, this_ind)

            self.timescale_data.points = np.delete(self.timescale_data.points, this_ind)
            self.timescale_data.worths = np.delete(self.timescale_data.worths, this_ind)

            # recalculate everything
            for ind in range(1,self.last_ind):
                self.pushButtons[ind].clicked.disconnect()
                self.pushButtons[ind].clicked.connect(self.remove_wrapper(ind))
                self.checkBoxs[ind].stateChanged.disconnect()
                self.checkBoxs[ind].stateChanged.connect(self.clickBox_wrapper(ind))
                self.lineEdits[ind].textChanged.disconnect()
                self.lineEdits[ind].textChanged.connect(self.score_changed_wrapper(ind))
            self.last_ind = len(self.hBoxs) - 1  # first row is 0
            self.timescale_data.todo_score = np.sum(self.timescale_data.points)
            # self.timescale_data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.lineEdits])
            self.update_text()
            self.progressBar.setValue(100 * self.timescale_data.todo_score / self.timescale_data.todo_goal)

        return remove_todo

    def score_changed_wrapper(self, this_ind):
        def on_score_changed():
            if self.checkBoxs[this_ind].isChecked():
                self.timescale_data.points[this_ind] = self.lineEdits[this_ind].text()
            self.timescale_data.todo_score = np.sum(self.timescale_data.points)
            self.timescale_data.worths[this_ind] = int(self.lineEdits[this_ind].text())

            # try:
            #     self.timescale_data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.lineEdits])
            # except ValueError:
            #     pass
        return on_score_changed

    def clickBox_wrapper(self, this_ind):
        def clickBox(state):
            if state == QtCore.Qt.Checked:
                self.add_points(this_ind)
            else:
                self.sub_points(this_ind)
        return clickBox

    def add_points(self, this_ind):
        self.timescale_data.points[this_ind] = int(self.lineEdits[this_ind].text())
        self.timescale_data.todo_score = np.sum(self.timescale_data.points)
        # self.timescale_data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.lineEdits])
        self.progressBar.setValue(100*self.timescale_data.todo_score/self.timescale_data.todo_goal)

    def sub_points(self, this_ind):
        self.timescale_data.points[this_ind] = 0
        self.timescale_data.todo_score = np.sum(self.timescale_data.points)
        # self.timescale_data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.lineEdits])
        self.progressBar.setValue(100*self.timescale_data.todo_score/self.timescale_data.todo_goal)

    def update_text(self):
        self.timescale_data.todos = [textEdit.toPlainText() for textEdit in self.textEdits]

    # def load(self):


class TimerWidget(QWidget):
    """ A class to display the historical data """

    TICK_TIME = 1  # 2 ** 6

    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.correct_lag = True

        self.break_mode = False
        self.pomodoro_duration = 25 * 60  # 3
        self.powerhour_duration = 60 * 60
        self.break_duration = 5 * 60
        self.dashboard.update_sec = 1
        self.dashboard.update_delay = 5
        self.pause_time = self.pomodoro_duration
        # self.reset = QPushButton('PyQt5 button', self)
        self.dashboard.reset.clicked.connect(self.do_reset)
        self.dashboard.power.clicked.connect(self.do_longreset)
        self.dashboard.start.clicked.connect(self.do_start)
        self.dashboard.break_2.clicked.connect(self.do_break)
        self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.setInterval(self.TICK_TIME)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.tick)
        self.do_reset()
        self.dashboard.spinBox.valueChanged.connect(self.update_goaltime)
        self.dashboard.label_8.setText(str(self.dashboard.data.pomodoros))
        self.disp_time()

    def load(self):
        pass

    def update_pomodoros(self):
        self.dashboard.data.pomodoros += 1
        self.dashboard.label_8.setText(str(self.dashboard.data.pomodoros))

    def update_goaltime(self):
        self.dashboard.data.goal_time = self.dashboard.spinBox.value()
        self.dashboard.reports.update_goals(self.dashboard.data.goals)

    @Qt.pyqtSlot()
    def do_start(self):
        self.timestamp_start = datetime.now()
        self.timer.start()
        self.dashboard.start.setText("Pause")
        self.dashboard.start.clicked.disconnect()
        self.dashboard.start.clicked.connect(self.do_pause)
        # if the code is puased and then unpaused update the final value of worktimehours
        if len(self.dashboard.data.work_time_hours) > 0:
            hour = self.timestamp_start.hour + self.timestamp_start.minute / 60. + self.timestamp_start.second / 3600
            self.dashboard.data.work_time_hours[-1] = hour


    @Qt.pyqtSlot()
    def do_pause(self):
        self.pause_time = self.time
        self.timer.stop()
        self.dashboard.start.setText("Start")
        self.dashboard.start.clicked.disconnect()
        self.dashboard.start.clicked.connect(self.do_start)

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

    def display(self):
        if self.time < 0:
            self.dashboard.lcd.setDigitCount(6)
            self.dashboard.lcd.display("-%d:%.2d" % (abs(self.time) // 60, abs(self.time) % 60))
        else:
            self.dashboard.lcd.setDigitCount(5)
            self.dashboard.lcd.display("%d:%.2d" % (self.time // 60, self.time % 60))

    @Qt.pyqtSlot()
    def tick(self):
        orig_time = self.time

        self.time -= self.TICK_TIME / 1000

        delta = datetime.now() - self.timestamp_start
        delta = delta.total_seconds()
        if self.break_mode:
            if np.int(self.time) != self.break_duration - np.int(delta):
                self.time = self.pause_time - np.int(delta)
        else:
            self.dashboard.data.work_time += self.TICK_TIME / 1000
            self.prog_time()
            self.disp_time()

            if self.correct_lag and np.int(self.time) != self.pomodoro_duration - np.int(delta):
                difference = self.time - (self.pause_time - np.int(delta))
                self.dashboard.data.work_time += difference
                self.time = self.pause_time - np.int(delta)

            #todo update to do it on every pmodoro_time interval
            #something like orig_time % self.pomodoro_time >= 0 and self.time % self.pomodoro_time < 0
            if orig_time >= 0 and self.time < 0:  # timer transitions below 0
                self.update_pomodoros()

            if orig_time//self.dashboard.update_sec != self.time//self.dashboard.update_sec:  # timer transitions past second mark
                diff_sec = orig_time//self.dashboard.update_sec - self.time//self.dashboard.update_sec
                self.update_work_time_times(int(np.round(diff_sec)))

            if orig_time//self.dashboard.update_delay != self.time//self.dashboard.update_delay:
                self.dashboard.reports.update_time_hist()

        self.display()

    def update_work_time_times(self, diff_sec):
        now = datetime.now()
        hour = now.hour+float(now.minute)/60. + now.second/3600

        if len(self.dashboard.data.work_time_hours) > 0 and diff_sec > 0:
            hours = np.linspace(self.dashboard.data.work_time_hours[-1], hour, diff_sec+1)[1:]
            work_times = np.linspace(self.dashboard.data.metrics_history[0][-1], self.dashboard.data.work_time/3600,
                                     diff_sec + 1)[1:]
            todo_scores = np.ones((diff_sec))*self.dashboard.data.daily.todo_score
            # print(np.round(diff_sec), self.dashboard.data.work_time_hours[-1], hour, hours)
        else:
            hours = hour
            work_times = self.dashboard.data.work_time/3600
            todo_scores = self.dashboard.data.daily.todo_score
        self.dashboard.data.work_time_hours = np.append(self.dashboard.data.work_time_hours, hours)
        tick_data = np.array([work_times, todo_scores, (
        todo_scores / self.dashboard.data.daily.todo_goal - work_times / self.dashboard.data.goal_time) * 100])

        if len(tick_data.shape) == 1:  # first instance is shape (3). This makes shape (3,1)
            tick_data = tick_data[:,np.newaxis]

        self.dashboard.data.metrics_history = np.append(self.dashboard.data.metrics_history, tick_data, axis=1)

        self.dashboard.reports.update_lineplots(diff_sec)
        # self.dashboard.reports.update_time_hist()

    def prog_time(self):
        self.dashboard.progressBar_2.setValue(self.dashboard.data.work_time/3600/self.dashboard.data.goal_time * 100)

    def disp_time(self):
        self.dashboard.label_4.setText('%d' % (self.dashboard.data.work_time/60))


class ErrandWidget(QWidget):
    def __init__(self, dashboard, scale):
        super().__init__()
        self.dashboard = dashboard
        comboBox = getattr(self.dashboard, f'{scale}_comboBox')
        errands = getattr(self.dashboard.data, scale).errands
        errands_groupBox = getattr(self.dashboard, f'{scale}_errands_groupBox')
        comboBox.addItems(str(errand) for errand in errands)
        # num_errands = len(self.data.daily_errands)
        # num_rows = num_errands//3
        # comboBox_row = num_rows if num_errands % 3 != 0 else num_rows+1
        comboBox.setGeometry(390, 125, 200, 31)
        comboBox.activated[str].connect(getattr(self, f'{scale}_check_errand'))
        for i in range(len(errands)):
            row = i // 3
            col = i % 3

            setattr(self.dashboard, f'{scale}_errands_label_{i}', QLabel(errands_groupBox))
            setattr(self.dashboard, f'{scale}_errand_pb_{i}', QProgressBar(errands_groupBox))

            errands_QLabel = getattr(self.dashboard, f"{scale}_errands_label_{i}")
            errands_QLabel.setText(str(errands[i]))
            errands_QLabel.setGeometry(col * 200 + 10, row * 30 + 30, 90, 16)

            errands_QProgressBar = getattr(self.dashboard, f"{scale}_errand_pb_{i}")
            errands_QProgressBar.setGeometry(col * 200 + 110, row * 30 + 30, 71, 20)
            errands_QProgressBar.setValue(0)

    def load(self):
        pass

    def daily_check_errand(self, text):
        errand_ind = np.where(text == self.dashboard.data.daily.errands)[0][0]
        self.prog_errand(errand_ind)
        self.dashboard.progressBar_3.setValue(self.dashboard.data.daily.errand_score)

    def weekly_check_errand(self, text):
        errand_ind = np.where(text == self.dashboard.data.weekly.errands)[0][0]
        self.prog_weekly_errand(errand_ind)
        self.dashboard.progressBar_4.setValue(self.dashboard.data.weekly.errand_score)

    def monthly_check_errand(self, text):
        errand_ind = np.where(text == self.dashboard.data.monthly.errands)[0][0]
        self.prog_weekly_errand(errand_ind)
        self.dashboard.progressBar_5.setValue(self.dashboard.data.monthly.errand_score)

    def prog_errand(self, errand_ind):
        progressbar = getattr(self.dashboard, f"daily_errand_pb_{errand_ind}")

        errand_amount = self.dashboard.data.daily.errand_amounts[errand_ind]
        errand_complete_yet = self.dashboard.data.daily.errand_scores[errand_ind] == 100  # errand_amount

        if errand_complete_yet:
            self.dashboard.data.daily.errand_score -= 100. / len(self.dashboard.data.daily.errands)
            self.dashboard.data.daily.errand_scores[errand_ind] = 0  # -= 100. / errand_amount
            progressbar.setValue(self.dashboard.data.daily.errand_scores[errand_ind])
        else:
            self.dashboard.data.daily.errand_score += 100. / (len(self.dashboard.data.daily.errands) * errand_amount)
            self.dashboard.data.daily.errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.dashboard.data.daily.errand_scores[errand_ind])

    def prog_weekly_errand(self, errand_ind):
        progressbar = getattr(self.dashboard, f"weekly_errand_pb_{errand_ind}")

        errand_amount = self.dashboard.data.weekly.errand_amounts[errand_ind]
        errand_complete_yet = self.dashboard.data.weekly.errand_scores[errand_ind] == 100  # errand_amount

        if errand_complete_yet:
            self.dashboard.data.weekly.errand_score -= 100. / len(self.dashboard.data.weekly.errands)
            self.dashboard.data.weekly.errand_scores[errand_ind] = 0  # -= 100. / errand_amount
            progressbar.setValue(self.dashboard.data.weekly.errand_scores[errand_ind])
        else:
            self.dashboard.data.weekly.errand_score += 100. / (len(self.dashboard.data.weekly.errands) * errand_amount)
            self.dashboard.data.weekly.errand_scores[errand_ind] += 100. / errand_amount
            progressbar.setValue(self.dashboard.data.weekly.errand_scores[errand_ind])
