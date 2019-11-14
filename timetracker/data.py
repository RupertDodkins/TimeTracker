""" This module hoasts the Data class used to store the user's scores and settings in gui """
import numpy as np

class Data():
    """ A class to store the data relevant for reports """

    def __init__(self):
        self.work_time = 0.
        self.pomodoros = 0
        self.goal_time = 8 * 25 * 60
        self.pomodoro_times = []
        self.work_time_hours = []
        self.work_time_history = []

        self.todo_score = 0
        self.todos = np.array([]*3)
        self.todos_complete = np.array([False,False,False])

        self.daily_errand_score = 0
        self.daily_errands = np.array(['Drink 3 bottles', 'Meditate', 'Tidy desk', 'Tidy room',
                              'NN', 'Update YNAB', 'Floss', 'Email to zero', 'In before 10am'])
        self.daily_errand_amounts = np.ones(len(self.daily_errands))
        self.daily_errand_amounts[self.daily_errands=='Drink 3 bottles']=3.#np.array([3.,1,1,1,1,1,2,1,1])
        self.daily_errand_amounts[self.daily_errands=='Floss']=2
        print(self.daily_errand_amounts)
        self.daily_errand_scores = np.zeros_like((self.daily_errand_amounts))

        self.weekly_errand_score = 0
        self.weekly_errands = np.array(['Gym', 'Gymnastics', 'Read paper', 'Get nice plot', 'Meal prep', 'Laundry'])
        self.weekly_errand_amounts = np.array([1,3.,1,1,1,4.])
        self.weekly_errand_scores = np.zeros_like((self.weekly_errand_amounts))
