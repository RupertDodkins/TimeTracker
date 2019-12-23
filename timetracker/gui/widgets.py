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
    def __init__(self, groupbox, data):

        self.groupbox = groupbox
        self.data = data

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

        self.vbox.addLayout(self.todo_hBoxs[0])
        self.progressBar = QProgressBar()
        self.progressBar.setValue(100*self.data.todo_score/self.data.todo_goal)
        self.progressBar.setGeometry(0,215,585,30)
        self.progressBar.setMinimumSize(585,30)
        self.progressBar.setMaximumSize(585,30)
        self.vbox.addWidget(self.progressBar)
        self.groupbox.setLayout(self.vbox)

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
        self.groupbox.setLayout(self.vbox)

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
            print(self.data.todo_score, self.data.todo_score, 'score')
            # self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
            self.update_todo_text()
            self.progressBar.setValue(100 * self.data.todo_score / self.data.todo_goal)

        return remove_todo

    def score_changed_wrapper(self, this_ind):
        def on_score_changed():
            if self.todo_checkBoxs[this_ind].isChecked():
                self.todo_points[this_ind] = self.todo_lineEdits[this_ind].text()
            self.data.todo_score = np.sum(self.todo_points)
            # try:
            #     self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
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
        self.todo_points[this_ind] = int(self.todo_lineEdits[this_ind].text())
        self.data.todo_score = np.sum(self.todo_points)
        # self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
        self.progressBar.setValue(100*self.data.todo_score/self.data.todo_goal)

    def sub_points(self, this_ind):
        self.todo_points[this_ind] = 0
        self.data.todo_score = np.sum(self.todo_points)
        # self.data.todo_goal = sum([int(lineEdits.text()) for lineEdits in self.todo_lineEdits])
        self.progressBar.setValue(100*self.data.todo_score/self.data.todo_goal)

    def update_todo_text(self):
        self.data.todos = [textEdit.toPlainText() for textEdit in self.todo_textEdits]


