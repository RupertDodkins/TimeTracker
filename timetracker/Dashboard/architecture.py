"""GUI architecture goes here"""

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QWidget, QPushButton, \
    QProgressBar, QRadioButton, QSlider, QLabel

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.pushButtonIn = QPushButton(self)
        self.pushButtonIn.setText("Clock In")
        self.pushButtonIn.clicked.connect(self.In_clicked)

        self.pushButtonOut = QPushButton(self)
        self.pushButtonOut.setText("Clock Out")
        self.pushButtonOut.clicked.connect(self.Out_clicked)

        self.topHPanel = QHBoxLayout()
        self.topHPanel.addWidget(self.pushButtonIn)
        self.topHPanel.addWidget(self.pushButtonOut)

        self.buttonParaWaveVBox = QVBoxLayout()
        self.buttonParaWaveVBox.addLayout(self.topHPanel)

        # Main layout
        self.parentHlayout = QHBoxLayout()
        self.parentHlayout.addLayout(self.buttonParaWaveVBox)

        self.setLayout(self.parentHlayout)

        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 1250
        self.title = 'Daily Dashboard'
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.show()

    @pyqtSlot()
    def In_clicked(self):
        print('not implemented')

    @pyqtSlot()
    def Out_clicked(self):
        print('not implemented')
