""" This module hoasts the Data class used to store the user's scores and settings in gui """
import numpy as np

class TimeScale():
    """ data common to daily, weekly and monthly objects. Read by Data """
    def __init__(self, errands, todos=[], todo_goal=100):
        self.errands = np.array(errands)
        self.todos = todos
        self.todo_goal = todo_goal

        self.todo_score = 0
        self.numtodos = 0
        self.errand_score = 0
        self.errand_amounts = np.ones((len(errands)))
        for i, errand in enumerate(self.errands):
            xloc = errand.find('x', -3)
            if xloc != -1:
                if len(errand)>xloc+2:
                    print("multiplier more than one digit or 'x' if different spot")
                    raise NotImplementedError
                self.errand_amounts[i] = errand[xloc+1]
        self.errand_scores = np.zeros((len(errands)))

class Data():
    """ A class to store the data relevant for reports """

    def __init__(self):
        self.daily = TimeScale(['Drink water x3', 'Meditate', 'Tidy desk', 'Tidy room',
                                 'NN', 'Update YNAB', 'Floss x2', 'Email to zero', 'In by 9.30am',
                                 'Phone Mum', 'No YouTube', 'No GUI code'])

        self.weekly = TimeScale(['Gym', 'Gymnastics x3', 'Read paper', 'Get nice plot',
                            'Meal prep', 'Laundry x4', 'Write todos'])

        self.monthly = TimeScale(['Pay Rent', 'Pay Credit Card', 'Pay STILT x2', 'Write todos'])

        self.work_time = 0.
        self.pomodoros = 0
        self.goal_time = 7 * 25 * 60
        self.pomodoro_times = []
        self.work_time_hours = []
        self.work_time_history = np.array([])

        self.efficiency_goal = -20  # it takes time to complete tasks

        self.goals = [self.goal_time, self.daily.todo_goal, self.efficiency_goal]
        self.goal_hours =  np.empty((3,0))
        self.start_goals = [0, 0, self.efficiency_goal]
        self.metrics_history = np.empty((3,0))
        self.metric_bins = [np.linspace(self.start_goals[0],self.goals[0],100),
                            np.linspace(self.start_goals[1],self.goals[1],100),
                            np.linspace(self.goals[2]-100,self.goals[2]+100,100) ]
        self.ylabels = ['Time worked (s)', 'Impact', 'Efficiency']



