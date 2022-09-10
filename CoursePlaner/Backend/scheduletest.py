
#to allow typehints in class definition
from __future__ import annotations
from dataclasses import dataclass

from inspect import isdatadescriptor
import math
from multiprocessing import set_forkserver_preload
from queue import PriorityQueue
from time import time
from tokenize import endpats
from tracemalloc import start

class timeobj:
    def __init__(self, hour: int, minute: int) -> None:
        caryover = math.floor(minute/60)
        self.minute = minute%60
        self.hour = hour + caryover

    def to_min(self):
        return self.hour*60 + self.minute
    
    def __add__(self,o):
        return timeobj(self.hour + o.hour, self.minute + o.minute)
    def __str__(self) -> str:
        return '{0:02d}'.format(self.hour) +':' +  '{0:02d}'.format(self.minute)
    def __mul__(self, rhs):
        if isinstance(rhs, int):
            return timeobj(self.hour*rhs, self.minute*rhs)
    def __rmul__(self,lhs):
        return self*lhs
    def __lt__(self,o):
        return (self.to_min() < o.to_min())
    def __le__(self,o):
        return (self.to_min() <= o.to_min())
    def __gt__(self,o):
        return (self.to_min() > o.to_min())
    def __ge__(self,o):
        return (self.to_min() >= o.to_min())

class timeslot:
    """
    Class that handles a timeslot within the calendar. Is used for resolving conflicts of shedules
    
    Args:
        id: Increasing id of timeslots
        starttime: time the slot starts
        slotlenght: time the slot takes 
        endtime: time the slot ends (automatically assigned via default slotlenght)
        relative_date: Day relative to Monday (0)
    """
    def __init__(self,starttime: timeobj ,relative_date: int, slotlenght = timeobj(1,0) ,endtime: timeobj = None, id = -1) -> None:
        #check for valid timedifference

        self.id = id
        self.starttime = starttime
        if endtime is None:
            self.endtime = self.starttime + slotlenght 
        else:
            self.endtime = endtime
        self.relative_date = relative_date
        self.modules:list[c_module] = []
        if self.endtime <= self.starttime:
            self.invalid = True
        else:
            self.invalid = False

    def __str__(self) -> str:
        return f"\t{self.starttime}-{self.endtime}; #{len(self.modules)}"

    def add_module(self, module_id):
        self.modules.append(module_id)
        return self


    def __lt__(self,o):
        '''
        Compares starttimes
        '''
        return self.starttime < o.starttime
    def __gt__(self,o):
        '''
        Compares starttimes
        '''
        return self.starttime > o.starttime
    def __eq__(self,o):
        '''
        Compares starttimes
        '''
        return self.starttime == o.starttime
    

    def __and__(self,o) -> timeslot:
        '''
        returns a timeslot with the overlap of self and o  
        if there is no overlap returns a timeslot with the invalid flag set
        ''' 
        return timeslot(max(self.starttime,o.starttime), min(self.endtime,o.endttime))

    #a = [timeslot(timeobj(0,0),0,timeobj(3,0)), timeslot(timeobj(4,0),0,timeobj(2,0)),timeslot(timeobj(8,0),0,timeobj(4,0))] 
    #b = [timeslot(timeobj(2,0),0,timeobj(3,0)), timeslot(timeobj(5,0),0,timeobj(4,0)),timeslot(timeobj(10,0),0)]
    @staticmethod
    def find_overlap(a:list[timeslot], b:list[timeslot]) -> list[timeslot]:
        '''
        Takes two sorted lists of timeslots and returns the overlapping slots

        '''
        #TODO: Write unittests
        #assume the timeslots are sorted
        pass
        overlaps:list[timeslot] = []
        #Sweepline

        #find all startingpoints in order (mergesort)
        i = 0
        j = 0
        startpoints:list[timeobj] = []
        while(i < len(a) and j < len(b)):
            if(a[i].starttime<b[j].starttime):
                startpoints.append(a[i].starttime)
                i += 1
            else:
                startpoints.append(b[j].starttime)
                j += 1
        while(i < len(a)):
            startpoints.append(a[i].starttime)
            i += 1
        while(j < len(b)):
            startpoints.append(b[j].starttime)
            j += 1
        #find all endpoints in order (mergesort)
        i = 0
        j = 0
        endpoints:list[timeobj] = []
        while(i < len(a) and j < len(b)):
            if(a[i].endtime<b[j].endtime):
                endpoints.append(a[i].endtime)
                i += 1
            else:
                endpoints.append(b[j].endtime)
                j += 1
        while(i < len(a)):
            endpoints.append(a[i].endtime)
            i += 1
        while(j < len(b)):
            endpoints.append(b[j].endtime)
            j += 1

        i = 0
        j = 0
        intervals:list[timeslot] = []
        curr_interval:timeslot 
        in_interval = False
        in_double_interval = False
        while(i < len(startpoints) and j < len(endpoints)):
            if(startpoints[i]<endpoints[j]):
                if in_interval:
                    in_double_interval = True
                    curr_interval = timeslot(startpoints[i],a[0].relative_date,endtime=endpoints[j])
                in_interval = True    
                i += 1
            else:
                if in_interval and not in_double_interval:
                    in_interval = False
                    j +=1
                    continue
                if in_double_interval:
                    in_double_interval = False
                    curr_interval = timeslot(curr_interval.starttime,a[0].relative_date,endtime=endpoints[j])
                    intervals.append(curr_interval)
                    j += 1

        #Take next endpoint to tie off overlap
        curr_interval = timeslot(curr_interval.starttime,a[0].relative_date,endtime=endpoints[j])
        intervals.append(curr_interval)


        return intervals




class day:
    """
    Manages many timeslots (Deprecated)
    """
    def __init__(self, relative_date:int, first_slot:timeobj, timeslots_per_day = 24, slotlength = timeobj(1,0), daynames:list[str] = None) -> None:
        self.timeslots_per_day = timeslots_per_day
        self.slotlength = slotlength
        self.relative_date = relative_date
        self.first_slot = first_slot
        self.daynames = daynames

        self.slots = [timeslot(self.first_slot + (i*self.slotlength), self.relative_date) for i in range(self.timeslots_per_day)]
    def __str__(self) -> str:
        if(self.daynames is not None) and (len(self.daynames) >= self.relative_date):
            
            return f"rel_dat:{self.daynames[self.relative_date]}"
        else:
            return f"rel_dat:{self.relative_date}"
    #Returns a list of overlaps between two days 
    def __and__(self, o):
        raise NotImplementedError 
        pass
@dataclass
class slot_boundry:
    time:timeobj
    modules:PriorityQueue
    def __lt__(self, other):
        return self.time< other.time
    

class n_day:
    """
     Manages many timeslots in a day
    """
    def __init__(self, relative_date:int, timeslots:list[timeslot] = None, daynames:list[str] = None) -> None:
        self.relative_date = relative_date
        self.daynames = daynames
        
        self.module_combos = []
        for slot in timeslots:
            self.add_timeslots(slots = [slot])

    def add_timeslots(self, slots:list[timeslot]):
        #TODO: implement module combo so i can search for id
        active_slots = [(combo.id,False) for combo in self.module_combos]

        boundries:list[slot_boundry] = []
        #collect all boundries
        for slot in slots:
            sbound = slot_boundry(slot.starttime,slot.modules) 
            ebound = slot_boundry(slot.endtime,slot.modules)
            boundries.append(sbound)
            boundries.append(ebound)
        for combo in self.module_combos:
            for slot in combo:
                sbound = slot_boundry(slot.starttime,slot.modules) 
                ebound = slot_boundry(slot.endtime,slot.modules)
                boundries.append(sbound)
                boundries.append(ebound)

        boundries = sorted(boundries) 
        #TODO Tests
        for bound in boundries:
            pass


class place:
    """
    Everything one needs to know about the place of a lecture
    Classvariables:
        distances: Distance matrix, has stored at id1,id2 the distance between 1 & 2
    """ 
    
    distances: list[list[timeobj]]  

    def __init__(self, name:str, id:int) -> None:
        self.name = name
        self.id = id

    def __sub__(self, other):
        return place.distances[self][other]

    def __str__(self) -> str:
        return f"{self.name}"    
    

class c_module:
    """
    A submodule of a course (like a block of exercise sessions) 
    """
    def __init__(self, name:str, id:int, slots:list[timeslot], place: place, description:str = "") -> None:
        self.name = name
        self.id = id
        self.slots = slots
        self.place = place
    def __str__(self) -> str:
        base = f"{self.name} @ {self.place}"
        for slot in self.slots:
            base = base + "\n" + f"{slot}"
        return base
class course:
    """
    Bundles multiple c_modules together into one course
    """
    def __init__(self, name:str, id:str, modules:list[c_module]):
        self.name = name
        self.id = id
        self.modules = modules


class calendar:
    """
    Manages many days for a week (or multiple) for handy access


    """
    def __init__(self, first_slot: timeobj, slotlength = timeobj(1,0), timeslots_per_day = 24 ,numdays:int = 7, startday:int = 0) -> None:
        self.first_slot = first_slot
        self.timeslots_per_day = timeslots_per_day
        self.numdays = numdays
        self.startday = startday
        self.slotlength = slotlength

        #Generates the calendar
        self.days = [day(startday+i,self.first_slot,self.timeslots_per_day,self.slotlength) for i in range(self.numdays)]

    def add_module(self,module: c_module):
        #iterate over every slot of this module and add the module to slots within the calendar that are touched by this 
        for slot in module.slots:
            curr_day = self.days[slot.relative_date]

            #find overlapping hours today
            overlaps = timeslot.find_overlap(curr_day.slots,module.slots)

            #Add the overlaps to the affected whole slots in day
            #REVISIT: this might be improvable by only taking care of the overlaps seperately
            
            #TODO: Remove system with slots in a day and replace with dynamic slots, which are created by merging different modules
            # Example: Everytime a new module is added, it is overlapped with the previous modules. The least common divisor is calculated and the plan is split up into the different slots. each slot is fully one combination of modules. This allows for easy conflict management.  

mod = c_module("analysis", 1, [timeslot(timeobj(i,10),1) for i in range(8)], place("HCI",1))



