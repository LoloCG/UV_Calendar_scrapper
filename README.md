# Description
Web scrapper for obtaining the dynamic class schedule for the University of Valencia, due to as of 18/9/24 not having API nor export option to obtain it.

## Differences with old manual import
The result is very similar to what it was with the manual import from the file that was given by the old platform of the University. 

Still, there are differences that make this option superior:
- This method displays the importance of Seminars and Lab Sessions by indicating them before the name of the Subject.
- This also obtains the calendar from the events that are created by the professors (exams, tests, assignments...).
- The events dont display Subject and Group IDs, which clutter the view of the Calendar.

Resulting calendar in Google Calendar:
![Resulting Calendar in Google Calendar](google_calendar_result.png)

# Table of Contents
- [Description](#description)
  - [Differences with old manual import](#differences-with-old-manual-import)
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
  - [Dependencies](#dependencies)
- [Usage](#usage)

# Installation
## Dependencies
Before running the project, make sure to install the necessary dependencies. You can install all of them directly using the command:

    pip install -r requirements.txt

# Usage
Example terminal output (from VSCode):
![terminal example text](terminal_example.png)

