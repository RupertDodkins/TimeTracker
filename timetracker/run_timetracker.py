import sys
from PyQt5 import QtWidgets
import main
from timetracker.Dashboard.architecture import Dashboard

def run_dashboard():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Dashboard')
    main = Dashboard()
    main.show()
    app.exec_()

if __name__=="__main__":
    run_dashboard()