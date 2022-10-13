from StudyplanerScraper.main import *
from CoursePlaner.Backend.scheduletest import *

courses = get_courses_format(["551-1402-00L","551-0307-00L","551-0307-01L", "401-2813-00L","401-0241-00L"],"2022W")

for course in courses:
    for module in course.modules:
        print(module)