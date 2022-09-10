from .scheduletest import *

def test_n_day_timeslots():
    a = [timeslot(timeobj(i,0),0).add_module(1) for i in range(4)]
    b = [timeslot(timeobj(i,0),0).add_module(2).add_module(4) for i in range(3,8)]

    monday = n_day(0,a)
    monday.add_timeslots(b)  