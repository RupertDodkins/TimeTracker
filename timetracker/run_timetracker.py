#!/Users/dodkins/PythonProjects/TimeTracker/venv/bin/python

import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtGui import QIcon, QPixmap
import timetracker.gui.breeze_resources
from timetracker.gui.dashboard import Dashboard

def run_dashboard():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Dashboard')
    app.setWindowIcon(QIcon(QPixmap('icon.jpg')))
    main = Dashboard()

    # set stylesheet
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
    main.show()
    app.exec_()

if __name__=="__main__":
    run_dashboard()
