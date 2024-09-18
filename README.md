# Description
Web scrapper for obtaining the dynamic class schedule for the University of Valencia, due to as of 18/9/24 not having API nor export option to obtain it.

# Differences with old manual import from Aulavirtual
The result is very similar to what it was with the manual import from the file that was given by the old platform of the University. 

However, there are several key improvements that make this solution superior:
- This method displays the importance of Seminars and Lab Sessions by indicating them before the name of the Subject.
- This also obtains the calendar from the events that are created by the professors (exams, tests, assignments...).
- The events dont display Subject and Group IDs, which clutter the view of the Calendar.

**Resulting calendar in Google Calendar:**
![Resulting Calendar in Google Calendar](images\google_calendar_result.png)

# Installation
The .exe file can be downloaded through the latest [release page](https://github.com/LoloCG/UV_Calendar_scrapper/releases/), or directly from [here](https://github.com/LoloCG/UV_Calendar_scrapper/releases/download/v1.2/main.exe)

The .exe is a portable executable, meaning it does not require installation—just download and run it.


# Usage
Running the .exe file will launch a terminal interface where you need to enter your AulaVirtual UV credentials (username and password).

- If you're using a MacBook, the script will automatically use Safari as the browser.
- On Windows and Linux, you’ll have the option to choose between Chrome and Firefox.

The script will then log into AulaVirtual and retrieve your personal schedule calendar, along with events created by professors in Aules. Once all the data is collected, it will generate a single .ics file, which can be imported into any preferred calendar application.

Note: it is common for the program to take a while when opening the Login page and Home, as the whole AulaVirtual Webpage framework has to load many dynamic elements. 

**Example terminal output (from VSCode)**
![terminal example text](images\ExampleTerminal.png)

