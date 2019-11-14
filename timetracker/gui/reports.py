""" This module hoasts the Data class used to store the user's scores and settings in gui """
import matplotlib.pylab as plt
import numpy as np
import time
from timetracker.logs import Logger
from matplotlib.figure import Figure
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.image import AxesImage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QFormLayout

class Reporter(QWidget):
    """ A class to display the historical data """

    def __init__(self, parent=None, nrows=2, ncols=1):
        super(Reporter, self).__init__(parent)

        self.data = parent.data

        self.nrows, self.ncols = nrows, ncols
        self.figure = Figure(figsize=(4*ncols,3*nrows))
        self.figure.subplots_adjust(left=0.175, bottom=0.1, right=0.89, top=0.9, wspace=0.005, hspace=0.2)

        # self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        gs = gridspec.GridSpec(self.nrows, self.ncols)

        for r in range(self.nrows):
            for c in range(self.ncols):
                self.figure.add_subplot(gs[r,c])

        self.axes = np.array(self.figure.axes).reshape(self.nrows, self.ncols)
        self.cax = []

        self.layoutVertical = QFormLayout(self)
        self.layoutVertical.addWidget(self.toolbar)
        self.layoutVertical.addWidget(self.canvas)

        self.ims = np.empty((self.nrows, self.ncols), dtype=AxesImage)

        # self.time = time.time()
        self.day_hours = np.arange(8, 23, 0.25)
        self.ts_loc = [0,0]

    def initialize_time_served(self):
        goal_hours = np.linspace(0,self.data.goal_time/60,len(self.day_hours))
        self.ts_goalline = self.axes[self.ts_loc[0],self.ts_loc[1]].plot(self.day_hours, goal_hours, linestyle='--', color='k')
        self.axes[self.ts_loc[0],self.ts_loc[1]].set_xlabel('clock time (hours)')
        self.axes[self.ts_loc[0],self.ts_loc[1]].set_ylabel('time worked (mins)')

    def update_goal_line(self, goal_time):
        self.ts_goalline.pop(0).remove()
        self.data.goal_time = goal_time
        goal_hours = np.linspace(0, self.data.goal_time/60, len(self.day_hours))
        self.axes[self.ts_loc[0],self.ts_loc[1]].set_ylim(0,self.data.goal_time/60)
        self.ts_goalline = self.axes[self.ts_loc[0],self.ts_loc[1]].plot(self.day_hours, goal_hours, linestyle='--', color='k')

    def update_time_served(self, x=0, y=0):
        self.axes[self.ts_loc[0],self.ts_loc[1]].plot(self.data.work_time_hours, np.array(self.data.work_time_history)/60, color='b')
        self.canvas.draw()
        # plt.show(block=True)
