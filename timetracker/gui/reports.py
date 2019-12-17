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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from datetime import datetime

class Reporter(QWidget):
    """ A class to display the historical data """

    def __init__(self, parent=None, nrows=3, ncols=2):
        super(Reporter, self).__init__(parent)

        self.data = parent.data
        self.start_hour_val=datetime.now().hour if datetime.now().hour>9 else 9
        self.stop_hour_val=24 if datetime.now().hour>17 else 17
        self.frac_hour_val=0.25

        self.nrows, self.ncols = nrows, ncols
        self.figure = Figure(figsize=(4*ncols,3*nrows))
        # self.figure.subplots_adjust(left=0.175, bottom=0.1, right=0.89, top=0.9, wspace=0.005, hspace=0.2)

        # self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        gs = gridspec.GridSpec(self.nrows, self.ncols)

        for r in range(self.nrows):
            for c in range(self.ncols):
                if r == 0 and c == 0:
                    ax0 = self.figure.add_subplot(gs[r,c])
                else:
                    ax = self.figure.add_subplot(gs[r,c], sharex = ax0)

        self.axes = np.array(self.figure.axes).reshape(self.nrows, self.ncols)
        self.cax = []

        self.reportsHBox = QHBoxLayout()
        start_combo = QComboBox()
        stop_combo = QComboBox()
        frac_combo = QComboBox()
        start_label = QLabel()
        stop_label = QLabel()
        frac_label = QLabel()

        start_combo.addItems(str(h) for h in range(24))
        stop_combo.addItems(str(h) for h in range(1,25))
        frac_combo.addItems(str(f) for f in 1./np.array([2,4,8,16]))
        start_label.setText('Start Hour')
        stop_label.setText('End Hour')
        frac_label.setText('Increment Fraction')
        start_combo.setCurrentText(str(self.start_hour_val))
        stop_combo.setCurrentText(str(self.stop_hour_val))
        frac_combo.setCurrentText(str(self.frac_hour_val))


        start_combo.activated[str].connect(self.update_start)
        stop_combo.activated[str].connect(self.update_stop)
        frac_combo.activated[str].connect(self.update_frac)

        self.reportsHBox.addWidget(start_label)
        self.reportsHBox.addWidget(start_combo)
        self.reportsHBox.addWidget(stop_label)
        self.reportsHBox.addWidget(stop_combo)
        self.reportsHBox.addWidget(frac_label)
        self.reportsHBox.addWidget(frac_combo)

        self.layoutVertical = QVBoxLayout(self)
        self.layoutVertical.addLayout(self.reportsHBox)
        self.layoutVertical.addWidget(self.toolbar)
        self.layoutVertical.addWidget(self.canvas)

        self.ims = np.empty((self.nrows, self.ncols), dtype=AxesImage)

        # self.time = time.time()
        self.day_hours = np.arange(self.start_hour_val, self.stop_hour_val, self.frac_hour_val)
        self.actual_day_hours = np.arange(datetime.now().hour+float(datetime.now().minute)/60, 23, 0.25)
        self.ts_hist_loc = [0,1]
        self.completed_lines = [None, None, None]
        self.ts_hist = None

        self.initialize_lineplots()
        self.initialize_time_hist()
        self.figure.tight_layout()  # why does this have to be here to not ignore the axis labels?
        self.figure.subplots_adjust(top=0.965, bottom=0.1, left=0.17, right=0.971, hspace=0, wspace=0.34)

    def update_start(self, text):
        self.start_hour_val = int(text)
        self.day_hours = np.arange(self.start_hour_val, self.stop_hour_val, self.frac_hour_val)
        self.update_goals(self.data.goals)

    def update_stop(self, text):
        self.stop_hour_val = int(text)
        self.day_hours = np.arange(self.start_hour_val, self.stop_hour_val, self.frac_hour_val)
        self.update_goals(self.data.goals)

    def update_frac(self, text):
        self.frac_hour_val = float(text)
        self.day_hours = np.arange(self.start_hour_val, self.stop_hour_val, self.frac_hour_val)
        self.update_goals(self.data.goals)

    def initialize_lineplots(self):
        self.goal_lines = []
        for y in range(2):
            axes = self.axes[:,y]
            for i, start, goal, ax, ylabel in zip(range(len(self.data.goals)), self.data.start_goals, self.data.goals,
                                                  axes, self.data.ylabels):

                if i == 2:
                    ax.set_xlabel('Clock time (hours)')
                else:
                    plt.setp(ax.get_xticklabels(), visible=False)

                if y==0:
                    goal_steps = np.linspace(start, goal, len(self.day_hours))  # factor of 3600 will be from here
                    self.goal_lines.append(ax.plot(self.day_hours, goal_steps, linestyle='--', color='k'))
                    ax.set_ylabel(ylabel)
                else:
                    ax.set_ylabel('Amount')
                ax.legend()

    def update_goals(self, goals):
        for ig, line, start, goal, ax in zip(range(len(self.data.goals)), self.goal_lines, self.data.start_goals, goals, self.axes[:,0]):
            line.pop(0).remove()
            self.data.goals[ig] = goal
            goal_steps = np.linspace(start, goal, len(self.day_hours))  #factor of 3600 will be from here
            ax.set_ylim(0,goal)
            self.goal_lines[ig] = ax.plot(self.day_hours, goal_steps, linestyle='--', color='k')

    def update_lineplots(self):
        for ig, line, ax, goal, metric in zip(range(len(self.data.goals)), self.completed_lines, self.axes[:,0],
                                               self.data.goals, self.data.metrics_history):
            if line is not None:
                line.remove()
            ax.collections.clear()
            self.completed_lines[ig],  = ax.plot(self.data.work_time_hours, metric, color='b')

            # todo implement this
            # current_goal = goal * (self.data.work_time_hours[-1]-self.start_hour_val)/(self.stop_hour_val - self.start_hour_val)
            # goal_hours = np.linspace(0, current_goal, len(self.data.work_time_hours))
            # self.axes[self.ts_loc[0],self.ts_loc[1]].fill_between(self.data.work_time_hours,
            #                                                       np.array(self.data.work_time_history)/3600, goal_hours,
            #                                                       label='Surviving', facecolor='red', alpha=0.5)
            # print(self.data.work_time_hours,np.array(self.data.work_time_history)/3600, goal_hours)
            self.canvas.draw()
            # line.pop(0).remove()
            # plt.show(block=True)

    def initialize_time_hist(self):
        # self.axes[self.ts_hist_loc[0],self.ts_hist_loc[1]].set_xlabel('Clock time (hours)')
        self.axes[self.ts_hist_loc[0],self.ts_hist_loc[1]].set_ylabel('Amount')

    def update_time_hist(self):
        # print(self.data.work_time_history)
        # print(np.histogram(self.data.work_time_history/3600, bins=self.day_hours))
        if self.ts_hist is not None:
            [b.remove() for b in self.ts_hist]
        _, _, self.ts_hist = self.axes[self.ts_hist_loc[0],self.ts_hist_loc[1]].hist(self.data.work_time_hours, bins=self.day_hours, color='b')
        self.canvas.draw()
        # hist.pop(0).remove()
