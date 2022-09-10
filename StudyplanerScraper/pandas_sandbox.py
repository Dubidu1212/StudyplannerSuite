import sched
from typing import List
import pandas as pd
import numpy as np


#dimensions: Weekday, Course, Hour
weekdays = ["Mo","Di","Mi","Do","Fr"]
hours = [str(i) for i in range(0,25)]
courses = ["a", "l"]

schedule = np.empty((5,25),dtype=object)
for wd_i,wd in enumerate(weekdays):
    for h_i,h in enumerate(hours):
        for c in courses:
            if schedule[wd_i,h_i] is None:
                schedule[wd_i,h_i] = [c]
            else:
                schedule[wd_i,h_i].append(c)
            pass

print(schedule)
print([i for i in range(0)])