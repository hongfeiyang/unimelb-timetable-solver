from csp import *
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import sys
from datetime import datetime
from collections import namedtuple


def is_in_range(time_tuple):
    
    if properties[time_tuple[0]]["Start Time"] <= time_tuple[1] and properties[time_tuple[0]]["End Time"] >= time_tuple[2]:
        return True
    
    return False
    

def has_overlap(a, b):
        
    # assume a and b are in the same day, because I have not seen any class that goes beyond 12AM, if so this university is crazy!
    if a[0] != b[0]:
        return False

    Range = namedtuple('Range', ['start', 'end'])

    a_start = a[1].split(":")
    a_end = a[2].split(":")
    b_start = b[1].split(":")
    b_end = b[2].split(":")

    r1 = Range(start=datetime(2000, 1, 1, int(a_start[0]), int(a_start[1]), 0), end=datetime(2000, 1, 1, int(a_end[0]), int(a_end[1]), 0))
    r2 = Range(start=datetime(2000, 1, 1, int(b_start[0]), int(b_start[1]), 0), end=datetime(2000, 1, 1, int(b_end[0]), int(b_end[1]), 0))

    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    delta = (earliest_end - latest_start).total_seconds()
    overlap = max(0, delta)

    return overlap != 0


def timetable_constraints(A, a, B, b):
    if not has_overlap(a, b) and is_in_range(a) and is_in_range(b):
        return True

    return False



class TimetableCSP(CSP):
    
    def __init__(self, subjectCodes, year, semester):
        
        self.domain = self.make_domain(subjectCodes, year, semester)
        self.neighbours = self.make_neighbours(self.domain)
        
        super().__init__(list(self.domain.keys()), self.domain, self.neighbours, timetable_constraints)
    
    
    def make_domain(self, subjectCodes, year, semester):

        vars = {}

        ### return a dataframe of the specified timetable if found, or return None if this timetable does not exist
        def get_subject_timetable(subjectCode, year, semester):

            url = "https://sws.unimelb.edu.au/"+str(year)+"/Reports/List.aspx?objects="+subjectCode+"&weeks=1-52&days=1-7&periods=1-56&template=module_by_group_list"
            html = urlopen(url)
            soup = BeautifulSoup(html, 'lxml')
            soup.find_all('table')
            table = str(soup.find_all("table"))
            df = pd.read_html(str(table))

            for _df in df:
                if semester in _df.iloc[0,0]:
                    return _df

            return None
        
        
        ### update vars to contain new subject class types and time slots
        def parse_problem(subjectCode, df):

            cols = df.columns

            for _key, _val in df.groupby(cols[1]):

                key = subjectCode + " " + _key

                domain_for_this_var = []

                for index, val in _val.iterrows():
                    entry = (val["Day"], val["Start"], val["Finish"], val["Class/Events"], val["Location"])
                    domain_for_this_var.append(entry)

                vars[key] = domain_for_this_var

            return None
        
        for subjectCode in subjectCodes:
            
            timetable = get_subject_timetable(subjectCode, year, semester)
            
            if timetable is None:
                print("The timetable you are looking for: ({} {} {}) does not exist".format(subjectCode, year, semester))
                sys.exit(1)
            
            parse_problem(subjectCode, timetable)

        return vars
    
    
    def make_neighbours(self, domain):
    
        keys = list(domain.keys())

        neighbours = {}

        for i in range(len(keys)):
            neighbours[keys[i]] = keys[:i] + keys[i+1:]

        return neighbours
    
    
    def display_timetable(self, solution):

        ps_time_key = dict((y,x) for x,y in solution.items())

        DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        TIMES = ["{:02d}:00".format(i) for i in range(7, 14)] + ["14:00"] + ["{:02d}:15".format(i) for i in range(13, 23)]

        output = "{:11s}|".format("")


        for day in DAYS:
            output += "{:111s}".format(day)
            if day != DAYS[4]:
                output += "|"
        output += "\n"

        for i in range(1, len(TIMES)):

            if TIMES[i-1] == "14:00":
                continue

            output += "{}-{}|".format(TIMES[i-1], TIMES[i])

            for day in DAYS:
                key = (day, TIMES[i-1], TIMES[i])

                found = False
                for new_key in ps_time_key.keys():
                    if has_overlap(key, new_key):

                        #output += "{:30s}".format(ps_time_key[new_key])
                        output += "{:30s}".format(new_key[3]) + " "
                        output += "{:80s}".format(new_key[4])
                        found = True

                if not found:
                    output += "{:111s}".format("")

                if day != DAYS[4]:
                    output += "|"

            output += "\n"

        return output
    

def parse_keywords():
    
    option = input("Welcome, have you read the documentation of this program and understood the purpose of the 'properties.txt' file? Enter Y or N ").upper()
    
    while(option != "N" or option != "Y"):
    
        if option == "N":
            print("Please do so now. Come back later")
            sys.exit(1)
        elif option == "Y":
            print("Good, generating timetable for you, please wait...")
            break
        else:
            option = input("please enter Y or N ").upper()
    
    
    df = pd.read_csv("properties.txt")
    properties = df.iloc[:2,:].to_dict()

    subjects = [i.upper() for i in list(df.iloc[2]) if not pd.isnull(i)]
    year = int(df.iloc[3,0])
    semester = df.iloc[4,0].upper()

    for subject in subjects:
        if len(subject) != 9:
            print("You might have entered the wrong subject code: {}".format(subject))
            print("You just said you read the documentation! I suggest you to do so now if you lied earlier")

    if year < 2018:
        print("You might have entered the wrong year: {}".format(year))
        print("You just said you read the documentation! I suggest you to do so now if you lied earlier")

    if len(semester) != 3:
        print("You might have entered the wrong semester code: {}".format(semester))
        print("You just said you read the documentation! I suggest you to do so now if you lied earlier")
        
    return subjects, year, semester, properties


def main():

    timetablecsp = TimetableCSP(subjects, year, semester)
    solutions = backtracking_search(timetablecsp, order_domain_values=lcv, select_unassigned_variable=mrv, inference=mac)
    if solutions:
        output = timetablecsp.display_timetable(solutions)
        with open("output.txt", 'w') as output_file:
            output_file.write(output)
        print("Task completed, please check the output.txt file in the same directory. ITS BEST TO VIEW IN ***FULLSCREEN***")

    else:
        print("Constraints cannot be satisfied, check your properties.txt file and also make sure that these subjects can co-exist in the same semester")



if __name__ == "__main__":
    subjects, year, semester, properties = parse_keywords()
    main()