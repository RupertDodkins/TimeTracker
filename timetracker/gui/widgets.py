""" Currently all this functionality is part of architecture. Will host the widget for pomodoro stop watch """
import numpy as np
from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QProgressBar, QCheckBox, QTextEdit, QLineEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout, QShortcut

class TimerWidget():
    """ A class to display the historical data """

    def __init__(self):
        pass

class TodoWidget():
    def __init__(self, groupbox, timescale_data):

        self.groupbox = groupbox
        self.timescale_data = timescale_data

        self.last_ind = 0
        self.points = np.zeros((1))
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
        self.lineEdits[0].setText(f'{20}')
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

    def add_todo(self):
        this_ind = len(self.hBoxs)
        self.points = np.append(self.points,0)

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

            self.points = np.delete(self.points, this_ind)

            # recalculate everything
            for ind in range(1,self.last_ind):
                self.pushButtons[ind].clicked.disconnect()
                self.pushButtons[ind].clicked.connect(self.remove_wrapper(ind))
                self.checkBoxs[ind].stateChanged.disconnect()
                self.checkBoxs[ind].stateChanged.connect(self.clickBox_wrapper(ind))
                self.lineEdits[ind].textChanged.disconnect()
                self.lineEdits[ind].textChanged.connect(self.score_changed_wrapper(ind))
            self.last_ind = len(self.hBoxs) - 1  # first row is 0
            self.timescale_data.todo_score = np.sum(self.points)
            print(self.timescale_data.todo_score, self.timescale_data.todo_score, 'score')
            # self.timescale_data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.lineEdits])
            self.update_text()
            self.progressBar.setValue(100 * self.timescale_data.todo_score / self.timescale_data.todo_goal)

        return remove_todo

    def score_changed_wrapper(self, this_ind):
        def on_score_changed():
            if self.checkBoxs[this_ind].isChecked():
                self.points[this_ind] = self.lineEdits[this_ind].text()
            self.timescale_data.todo_score = np.sum(self.points)
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
        self.points[this_ind] = int(self.lineEdits[this_ind].text())
        self.timescale_data.todo_score = np.sum(self.points)
        # self.timescale_data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.lineEdits])
        self.progressBar.setValue(100*self.timescale_data.todo_score/self.timescale_data.todo_goal)

    def sub_points(self, this_ind):
        self.points[this_ind] = 0
        self.timescale_data.todo_score = np.sum(self.points)
        # self.timescale_data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.lineEdits])
        self.progressBar.setValue(100*self.timescale_data.todo_score/self.timescale_data.todo_goal)

    def update_text(self):
        self.timescale_data.todos = [textEdit.toPlainText() for textEdit in self.textEdits]


