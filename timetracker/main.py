import time
import numpy as np

class Clocker():
    def __init__(self):
        self.in_times = np.array([])
        self.out_times = np.array([])

    def clock_in(self, in_times):
        in_time = time.time()
        in_times.append(in_time)

    def clock_out(self, out_times):
        out_time = time.time()
        out_times.append(out_time)

    def calc_clocked_time(self):
        assert len(self.out_times) == len(self.in_times)
        self.clocked_times = self.out_times - self.in_times
        self.clocked_time = sum(self.clocked_times)

print('Running main')
clock = Clocker()
func_dict = {'Clocker':Clocker}
if __name__ == "__main__":
    command = input("> ")
    func_dict[command]()

