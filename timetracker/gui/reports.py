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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton
from datetime import datetime
import time

class ReportWidget(QWidget):
    """ A class to display the historical data """

    def __init__(self, parent=None, nrows=3, ncols=2):
        super(ReportWidget, self).__init__(parent)

        self.data = parent.data
        self.ncols = ncols

        self.start_hour_val = datetime.now().hour if datetime.now().hour > 9 else 9
        self.stop_hour_val = 24 if datetime.now().hour >= 17 else 17
        self.frac_hour_val = 0.5 #0.125

        self.nrows, self.ncols = nrows, ncols
        self.facecolor = (49./255,54./255,59./255)
        self.figure = Figure(figsize=(4*ncols,3*nrows), facecolor=self.facecolor)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        gs = gridspec.GridSpec(self.nrows, self.ncols, width_ratios=[3, 1], wspace=0.05)
        for r in range(self.nrows):
            for c in range(self.ncols):
                self.figure.add_subplot(gs[r, c])
        self.axes = np.array(self.figure.axes).reshape(self.nrows, self.ncols)
        self.axes[0,0].get_shared_x_axes().join(self.axes[0,0], self.axes[1,0], self.axes[2,0])
        for r in range(self.nrows):
            self.axes[r,0].get_shared_y_axes().join(self.axes[r,0], self.axes[r,1])

        self.cax = []

        self.reportsHBox = QHBoxLayout()
        start_combo = QComboBox()
        stop_combo = QComboBox()
        frac_combo = QComboBox()
        start_label = QLabel()
        stop_label = QLabel()
        frac_label = QLabel()
        zoom_buttom = QPushButton()

        start_combo.addItems(str(h) for h in range(24))
        stop_combo.addItems(str(h) for h in range(1,25))
        frac_combo.addItems(str(f) for f in 1./np.array([2,4,8,16]))
        start_label.setText('Start Hour')
        stop_label.setText('End Hour')
        frac_label.setText('Increment Fraction')
        start_combo.setCurrentText(str(self.start_hour_val))
        stop_combo.setCurrentText(str(self.stop_hour_val))
        frac_combo.setCurrentText(str(self.frac_hour_val))
        zoom_buttom.setText('Quick Zoom')

        start_combo.activated[str].connect(self.update_start)
        stop_combo.activated[str].connect(self.update_stop)
        frac_combo.activated[str].connect(self.update_frac)
        zoom_buttom.clicked.connect(self.quick_zoom)

        self.reportsHBox.addWidget(zoom_buttom)
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

        self.num_hours = (self.stop_hour_val-self.start_hour_val)/self.frac_hour_val
        self.day_hours = np.linspace(self.start_hour_val, self.stop_hour_val, self.num_hours)  #use linspace instead of arange to include the final value
        self.actual_day_hours = np.arange(datetime.now().hour+float(datetime.now().minute)/60, 23, 0.25)
        self.ts_hist_loc = [0,1]
        self.completed_lines = [None, None, None]
        self.completed_hists = [[None, None], [None, None],[None, None]]
        self.ts_hist = None

        self.initialize_plots()
        self.figure.tight_layout()  # why does this have to be here to not ignore the axis labels?
        self.figure.subplots_adjust(top=0.965, bottom=0.1, left=0.12, right=0.971, hspace=0, wspace=0.28)

        parent.horizontalLayout_2.addWidget(self)
        parent.reports_groupBox.setLayout(parent.horizontalLayout_2)

    def quick_zoom(self):
        xmin, xmax = self.data.work_time_hours[-1] + np.array([-2, 2])
        for y in range(3):
            self.axes[y, 0].set_xlim(xmin,xmax)
            # mins = np.array([np.min(self.data.metrics_history[y][-1]), self.data.start_goals[y]])
            # maxs = np.array([np.max(self.data.metrics_history[y][-1]), self.data.goals[y]])
            # ymin, ymax = np.array([min(mins), max(maxs)]) * np.array([0.5,1.5])
            # self.axes[y, 0].set_ylim(ymin,ymax)

    def update_start(self, text):
        self.start_hour_val = int(text)
        self.day_hours = np.linspace(self.start_hour_val, self.stop_hour_val, self.num_hours)
        self.update_goals(self.data.goals)

    def update_stop(self, text):
        self.stop_hour_val = int(text)
        self.day_hours = np.linspace(self.start_hour_val, self.stop_hour_val, self.num_hours)
        self.update_goals(self.data.goals)

    def update_frac(self, text):
        self.frac_hour_val = float(text)
        self.num_hours = (self.stop_hour_val - self.start_hour_val) / self.frac_hour_val
        self.day_hours = np.linspace(self.start_hour_val, self.stop_hour_val, self.num_hours)
        self.update_goals(self.data.goals)

    def initialize_plots(self):
        self.goal_lines = []
        for y in range(self.ncols):
            axes = self.axes[:,y]
            for i, start, goal, ax, ylabel in zip(range(len(self.data.goals)), self.data.start_goals, self.data.goals,
                                                  axes, self.data.ylabels):

                ax.tick_params(direction='in', color='w', labelcolor='w')
                for spine in ax.spines.values():
                    spine.set_edgecolor('w')
                ax.xaxis.label.set_color('w')
                ax.yaxis.label.set_color('w')
                ax.set_facecolor(self.facecolor)
                if i == 2 and y ==0:
                    ax.set_xlabel('Clock time (hours)')
                    ax.set_ylim(-self.data.daily.todo_goal,self.data.daily.todo_goal)
                if i < 2:
                    plt.setp(ax.get_xticklabels(), visible=False)

                if y==0:
                    goal_steps = np.linspace(start, goal, len(self.day_hours))  # factor of 3600 will be from here
                    self.goal_lines.append(ax.plot(self.day_hours, goal_steps, linestyle='--', color='w', linewidth=2))
                    ax.set_ylabel(ylabel)
                if i ==2 and y ==1:
                    ax.set_xlabel('Amount')
                if y ==1:
                    plt.setp(ax.get_yticklabels(), visible=False)

                # ax.legend()

    def update_goals(self, goals):
        for ig, line, start, goal, ax in zip(range(len(self.data.goals)), self.goal_lines,
                                             self.data.start_goals, goals, self.axes[:,0]):
            line.pop(0).remove()
            self.data.goals[ig] = goal
            goal_steps = np.linspace(start, goal, len(self.day_hours))
            ax.set_ylim(0,goal)
            self.goal_lines[ig] = ax.plot(self.day_hours, goal_steps, linestyle='--', color='w', linewidth=2)
            if ig == 2:
                ax.set_ylim(-self.data.daily.todo_goal, self.data.daily.todo_goal)
            m = goal / (self.stop_hour_val - self.start_hour_val)
            current_goal = m * (self.data.work_time_hours - self.start_hour_val)
            self.data.goal_hours[ig] = current_goal

    def update_lineplots(self, diff_sec):
        """
        During each TimerWidget.tick a (or several) data point(s) are added to the plots

        Parameters
        ----------
        diff_sec : int
                   the number of seconds since the code last updated (because of mac background mode)
        """
        current_goals = []
        for ig, line, ax, goal, metric in zip(range(len(self.data.goals)), self.completed_lines, self.axes[:,0],
                                               self.data.goals, self.data.metrics_history):
            if line is not None:
                line.remove()
            ax.collections.clear()
            self.completed_lines[ig],  = ax.plot(self.data.work_time_hours, metric, color=(64./255,173./255,233./255),
                                                 linewidth=2)

            m = goal/(self.stop_hour_val - self.start_hour_val)
            new_inds = (diff_sec+1) if diff_sec > 0 else 2
            current_goal = m * (self.data.work_time_hours[-new_inds:]-self.start_hour_val)
            current_goals.append(current_goal)
            # self.data.goal_hours[ig] = np.append(self.data.goal_hours[ig, :-1], current_goal)

            goal_hours = np.append(self.data.goal_hours[ig, :-1], current_goal)
            # ax.plot(self.data.work_time_hours, self.data.goal_hours[ig], color='orange', marker='o')

            ax.fill_between(self.data.work_time_hours, metric, goal_hours,
                            where=goal_hours >= metric, facecolor='orangered',
                            interpolate=True)

            ax.fill_between(self.data.work_time_hours, metric, goal_hours,
                            where=goal_hours <= metric, facecolor='lime',
                            interpolate=True)

            self.canvas.draw()


        self.data.goal_hours = np.append(self.data.goal_hours[:, :-1], current_goals, axis=1)

    def update_time_hist(self):
        for ig, hist, ax, metric, bins in zip(range(len(self.data.goals)), self.completed_hists, self.axes[:,1],
                                        self.data.metrics_history, self.data.metric_bins):

            if not None in hist:
                [b.remove() for b in hist]
            ax.collections.clear()

            #todo make not slow by only operating on the current bin

            # now = datetime.now()
            # current_bin = now.hour+now.minute/60+now.second/3600 == bins
            # print(current_bin)
            # where_thrive = self.data.goal_hours[ig] <= metric
            # metric_heights, _ = np.histogram(metric, bins=bins)
            # survive_heights, thrive_heights = np.array(
            #     [(sum(b == False), sum(b == True)) for b in np.split(where_thrive, np.cumsum(metric_heights))]).T
            # self.completed_hists[ig][0] = ax.barh(bins, thrive_heights, height=2, color='springgreen')
            # self.completed_hists[ig][1] = ax.barh(bins, survive_heights, left=thrive_heights, height=2, color='orangered')

            start = time.time()
            where_thrive = self.data.goal_hours[ig] <= metric
            thrive = metric[where_thrive]
            survive = metric[~where_thrive]
            end = time.time()
            # print(ig, end - start)

            start = time.time()
            colors = ['lime', 'orangered']
            _, _, self.completed_hists[ig] = ax.hist([thrive, survive], bins=bins,
                                                     color=colors, orientation='horizontal', stacked=True)
            end = time.time()
            # print(ig, end - start)

            # start = time.time()
            # _, _, self.completed_hists[ig] = ax.hist(metric, bins=bins,
            #                                          color=(64./255,173./255,233./255), orientation='horizontal')
            # end = time.time()
            # print(ig, end - start)

            self.canvas.draw()

