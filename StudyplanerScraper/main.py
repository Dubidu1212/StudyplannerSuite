import sched
from sqlite3 import Timestamp
import requests
from html.parser import HTMLParser

import requests
from bs4 import BeautifulSoup

from typing import *


from unicodedata import normalize

#import pandas as pd
import numpy as np

from CoursePlaner.Backend.scheduletest import course, module


courses = ["529-0004-01L", "529-0004-01L"]
baseurl = "http://vvz.ethz.ch"

def find_HSFS(course):
    pass

def create_query(semester: str, lecture_code: str) -> str:
    #semester_codes = ["2022S","2022W"]
    basequery = "http://vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebot.view?lang=de&search=on&semkez=&studiengangTyp=&deptId=&studiengangAbschnittId=&lerneinheitstitel=&lerneinheitscode=&famname=&rufname=&wahlinfo=&lehrsprache=&periodizitaet=&katalogdaten=&_strukturAus=on&search=Suchen"
    basequery_list = basequery.split("&")

    #semester
    basequery_list[2] = basequery_list[2] + semester
    #lecture code
    basequery_list[7] = basequery_list[7] + lecture_code

    return '&'.join(basequery_list)

def query_for_course_url(query: str) -> Set[str]:
    website =  requests.get(query)
    content = website.text
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find_all("td",class_="border-no")
    #<tr><th>Nummer</th><th>Titel</th><th>Typ</th><th>ECTS</th><th colspan="2">Umfang</th><th>Dozierende</th></tr>
    links = []
    for elem in table:
        #get links to detailed page
        links.append(elem.parent.find("a",{"href": True}).get("href"))
    unique_links = set(links)

    return unique_links

class time_slot:

    def __init__(self,day, timespan, room):
        self.day = day
        self.timespan = timespan
        self.room = room
    def __str__(self):
        return self.day + " " + self.timespan + " " +  self.room[0] +" "+ self.room[1]
    #FIXME: add sanity check for string to int conversion
    def to_array(self):
        print(self.timespan)
        return [self.day, [int(i) for i in self.timespan.split("-")], self.room]

#TODO: implement etcs querry
class course_info:
    def __init__(self, c_number, c_type, time, schedule, course_link, etcs = None, prof = None, info = None):
        """
        Args:
            number
            type
            time
            schedule
            prof
            info
            courselink
        """
        self.number = c_number
        self.type = c_type
        self.time = time
        self.schedule: time_slot = schedule
        self.prof = prof
        self.info = info
        self.course_link = course_link
    def __str__(self):
        head =  "{0} {1}, T:{2}".format(self.number,self.type,self.time)
        sched = "\n \t- ".join([str(i) for i in self.schedule])
        return head + sched
    def to_array(self):
        return [self.number,self.type,self.time, [i.to_array() for i in self.schedule], self.prof, self.info]


#returns a list of course components with time and place
def query_detail_page(page_link: str) -> List[course_info]:
    """
    Description of query_detail_page

    Args:
        page_link (str): A string containing the link to the course page on vvz

    Returns:
        List[course_info]: Retruns a list of course parts. A course part acts like a seperate course (Lecture and Exercise are often separated)

    """
        
    website = requests.get(baseurl + page_link)
    content = website.text
    soup = BeautifulSoup(content, 'html.parser')

    #get blocks
    blocks = soup.find_all("table",class_="nested")
    unique_blocks_list = []
    for block in blocks:
        unique_blocks_list.append(block.parent.parent)

    unique_blocks = set(unique_blocks_list)
    course_parts = []
    for block in unique_blocks:
        #block is single row with all infos about course/exercise lessons
        columns = block.find_all("td", recursive = False)

        
        #course number
        course_number = columns[0].text.split(" ")[0]
        course_number = normalize('NFKD', course_number)

        #title
        title = columns[1].contents[0]
        #time
        time = columns[2].text
        time = normalize('NFKD', time) 
        #schedule
        timetable = columns[3].contents[0]

        last_day = None
        slots = []

        for row in timetable.contents:

            #get weekday
            if(len(row.contents[0].text) != 0):
                last_day = row.contents[0].text
            #get time
            timespan = row.contents[1].text
            #get room
                #tuple from building and room
            
            room_parts = row.contents[2].find_all("a")
            room = (room_parts[0].text, room_parts[1].text)

            timeslot = time_slot(last_day,timespan, room)
            slots.append(timeslot)
            
        
        #course link
        course_link = baseurl + page_link

        course = course_info(course_number,title,time,slots, course_link)
        course_parts.append(course)
    return course_parts


    
    


#TODO: create semester independent version

def get_courses_array(course_number_list: List[str], semester: str ) -> list:
    """
    Fetches the url's for the course numbers provided.
    Args:
        course_number_list (List[str],semester:str): A list of course numbers that should be fetched
        semester (str): A string of the semester in the format of "2022W"

    Returns:
        list

    """
    course_infos = []
    for course_number in course_number_list:
        query = create_query(semester, course_number)
        matching_courses_url = query_for_course_url(query)
        if len(matching_courses_url) == 0:
            print("Course {0} not found are you in the correct semester?".format(course_number))
        for mcu in matching_courses_url:
            details = query_detail_page(mcu)
            for course_part in details:
                course_infos.append(course_part.to_array())

    return course_infos

def get_courses(course_number_list: List[str], semester:str) -> List[course_info]:
    course_infos = []
    for course_number in course_number_list:
        query = create_query(semester, course_number)
        matching_courses_url = query_for_course_url(query)
        if len(matching_courses_url) == 0:
            print("Course {0} not found are you in the correct semester?".format(course_number))
        for mcu in matching_courses_url:
            details = query_detail_page(mcu)
            for course_part in details:
                course_infos.append(course_part)

    return course_infos

def get_courses_format(course_number_list: List[str], semester:str) -> List[course]:
    """
    Fetches courses and returns them in the format of course classes
    """
    courses:list[course] = []

    course_infos = []
    for course_number in course_number_list:

        query = create_query(semester, course_number)
        matching_courses_url = query_for_course_url(query)
        if len(matching_courses_url) == 0:
            print("Course {0} not found are you in the correct semester?".format(course_number))
        for mcu in matching_courses_url:
            details = query_detail_page(mcu)

            for course_part in details: 
                course_infos.append(course_part)

            #create modules
            for course_part in details:
                
                
                curr_module = c_module(course_part.type,course_part_it,"<slots>","<place>")
            
            curr_course = course("<add here the course name>",details.number,None)

    return course_infos 

#"551-1402-00L","551-0307-00L","551-0307-01L", "401-2813-00L",

#for course in get_courses_array([ "401-0241-00L"],"2022W"):
#    print(course)


    
weekdays = ["Mo","Di","Mi","Do","Fr","Sa","So"]
#TODO: keep entire data structure so the formated version can be adjusted acording to user
def create_schedule_raw(course_number_list, semester):
    c_arr = get_courses(course_number_list,semester)
    schedule = np.empty((7,25), dtype=object)
    for wd_i,wd in enumerate(weekdays):
        for course in c_arr:
            for date in course.schedule:

                #TODO: implement to also match DO/2w 
                date_arr = date.to_array()
                if wd in date_arr[0]:
                    #course is on the specified date

                    for hour in range(0,25):
                        if hour in range(date_arr[1][0], date_arr[1][1]):
                            #add this course to the hour it is taught in
                            if(schedule[wd_i,hour] is None):
                                schedule[wd_i,hour] = [course.type + str(date.room)]
                            else:
                                schedule[wd_i,hour].append(course.type + str(date.room))
    
    return schedule

def pad_array_for_csv(inarray, sep, length) -> str:
    if inarray is None:
        inarray = [] 
    if len(inarray) > length:
        print("ERROR: You are trying to pad an array to a shorter size")
        return
    outstr = ""
    for elem in inarray:
        outstr += elem + sep
    for i in range(max(length-len(inarray),0)):
        outstr += sep
    #also pad entirely empty cells
    if(length == 0):
        outstr += sep
    return outstr

def create_schedule_csv(course_number_list, semester, sep = ";"):
    raw_sched = create_schedule_raw(course_number_list, semester)

    #calculate conflicts 
    max_conflicts_on_day = [0 for i in weekdays]

    for day_i,day in enumerate(raw_sched):
        curr_conf = 0
        for hour in day:
            if hour is None:
                hour = []
            print(hour)
            curr_conf = max(curr_conf, len(hour))
        max_conflicts_on_day[day_i] = curr_conf
        print(curr_conf)

    raw_sched = np.swapaxes(raw_sched,0,1)

    

    
    #for each day find number of courses to find the minimal spacing    
    header = "h" + sep
    for day in range(len(max_conflicts_on_day)):
        header += weekdays[day] + sep
        for i in range(max(max_conflicts_on_day[day]-1,0)):
            header += sep
    body = ""

    for h_i, h in enumerate(raw_sched):
        
        body += str(h_i) + sep
        for d_i, d in enumerate(h):
            curr_courses = raw_sched[h_i,d_i]
            
            body += pad_array_for_csv(curr_courses,sep,max_conflicts_on_day[d_i])
        body += "\n"
    return header + "\n" + body

#print(create_schedule_raw([ "401-0241-00L"],"2022W"))
#print(create_schedule_csv(["551-1402-00L","551-0307-00L","551-0307-01L", "401-2813-00L",
# "401-0241-00L"],"2022W"))
#"551-1402-00L","551-0307-00L","551-0307-01L", "401-2813-00L",

#TODO: Create a dependency tree and a dependency solver to automatically generate mathcing shedules