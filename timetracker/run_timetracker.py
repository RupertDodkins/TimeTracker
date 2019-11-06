import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QFile, QTextStream
import timetracker.Dashboard.breeze_resources
from timetracker.Dashboard.architecture import Dashboard

def run_dashboard():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Dashboard')
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
