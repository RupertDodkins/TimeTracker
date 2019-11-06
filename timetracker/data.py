""" This module hoasts the Data class used to store the user's scores and settings in Dashboard """
import numpy as np

class Data():
    """ A class to store the data for a certain day """

    def __init__(self):
        self.work_time = 0.
        self.pomodoros = 0
        self.goal_time = 8 * 25 * 60
        self.pomodoro_times = []

        self.todo_score = 0
        self.todos = np.array([]*3)
        self.todos_complete = np.array([False,False,False])

        self.errand_score = 0
        self.errands = np.array(['Drink 3 bottles', 'Read paper', 'Get result for Ben', 'Meditate', 'NN',
                                 'Update YNAB', 'Tidy room', 'Floss', 'Email to zero'])
        self.errand_amounts = np.array([3., 1, 1, 1, 1, 1, 1, 2, 1])
        self.errand_scores = np.zeros_like((self.errand_amounts))


