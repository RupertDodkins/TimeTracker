""" This module hoasts the Data class used to store the user's scores and settings in Dashboard """
import matplotlib.pylab as plt
import numpy as np
import time
from timetracker.logs import Logger

class Reporter():
    """ A class to display the historical data """

    def __init__(self):
        self.logger = Logger()
        self.data = self.logger.data_load()
        self.time = time.time()

    def plot_clocked_time(clocked):
        plt.plot(clocked)
        plt.show(block=True)