# unimelb-timetable-solver
A tool to arrange timetable for Unimelb students

You need to install python 3.6 and above to run this program

Upon successful python installation, run
pip3 install pandas beautifulsoup4 lxml
to install the required packages.

You should specify all parameters in properties.txt file.

The first three lines tell the program your preferred start time and end time for each day in a week, e.g, if you want to go to school after 7 o'clock on Monday morning, you should put "07:00" (without quotation mark) after the first comma in the "Start Time" line. If you do not want to go to school on Friday, you could change the "End Time" field of Friday to "00:00" (without quotation mark). DO NOT put spaces between a time and a comma. Represent time in standard 24h hh:mm format.

You should enter your subject codes, separated by comma, after keyword "Subjects" in line #5.
Enter year after keyword "Year" in line #6, year >= 2019.
Enter the 3-digit semester code after keyword "Semester" in line #7, e.g. "SM1", "SM2", "SUM", "JUL" etc.

Only alter the fields you are required to change, DO NOT remove any comma in the properties.text file, DO NOT insert any unnecessary space to any field.

After you configured your properties.txt file, cd to the program's directory then run the program with
python3 timetable_solver.py

