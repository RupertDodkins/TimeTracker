""" This module hoasts the Data class used to store the user's scores and settings in gui """
import numpy as np

class Daily():
    """ Daily data read by Data """
    def __init__(self):
        self.todo_score = 0
        self.todos = []
        self.numtodos = 0
        self.todo_goal = 100
        self.todo_score = 0

        self.errand_score = 0
        self.errands = np.array(['Drink water x3', 'Meditate', 'Tidy desk', 'Tidy room',
                                 'NN', 'Update YNAB', 'Floss x2', 'Email to zero', 'In by 9.30am',
                                 'Phone Mum', 'No YouTube', 'No GUI code'])
        self.errand_amounts = np.ones(len(self.errands))
        self.errand_amounts[self.errands == 'Drink water x3'] = 3.  # np.array([3.,1,1,1,1,1,2,1,1])
        self.errand_amounts[self.errands == 'Floss x2'] = 2
        self.errand_scores = np.zeros_like((self.errand_amounts))

class Weekly():
    """ Weekly data read by Data """
    def __init__(self):
        self.todo_score = 0
        self.todos = []
        self.numtodos = 0
        self.todo_goal = 100
        self.todo_score = 0

        self.errand_score = 0
        self.errands = np.array(['Gym', 'Gymnastics x3', 'Read paper', 'Get nice plot',
                                 'Meal prep', 'Laundry x4', 'Write todos'])
        self.errand_amounts = np.array([1, 3., 1, 1, 1, 4., 1])
        self.errand_scores = np.zeros_like((self.errand_amounts))

class Monthly():
    """ Monhtly data read by Data """
    def __init__(self):
        self.todo_score = 0
        self.todos = []
        self.numtodos = 0
        self.todo_goal = 100
        self.todo_score = 0

        self.errand_score = 0
        self.errands = np.array(['Pay Rent', 'Pay Credit Card', 'Pay STILT x2', 'Write todos'])
        self.errand_amounts = np.array([1, 1, 2, 1])
        self.errand_scores = np.zeros_like((self.errand_amounts))


class Data():
    """ A class to store the data relevant for reports """

    def __init__(self):
        self.daily = Daily()
        self.weekly = Weekly()
        self.monthly = Monthly()

        self.work_time = 0.
        self.pomodoros = 0
        self.goal_time = 7 * 25 * 60
        self.pomodoro_times = []
        self.work_time_hours = []
        self.work_time_history = np.array([])

        self.efficiency_goal = 0

        self.goals = [self.goal_time, self.daily.todo_goal, self.efficiency_goal]
        self.goal_hours = [[],[],[]]
        self.start_goals = [0, 0, self.efficiency_goal]
        self.metrics_history = [[], [], []]
        self.metric_bins = [np.linspace(self.start_goals[0],self.goals[0],100),
                            np.linspace(self.start_goals[1],self.goals[1],100),
                            np.linspace(self.goals[2]-100,self.goals[2]+100,100) ]
        self.ylabels = ['Time worked (s)', 'Impact', 'Efficiency']



