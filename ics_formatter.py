import pandas as pd
from ics import Calendar

def convert_event_cal_ics_to_df():
    ics_file_path = 'event_calendar.ics'
    with open(ics_file_path, 'r') as f:
        calendar = Calendar(f.read())

    events = []
    for event in calendar.events:
        events.append({
            'name': event.name,
            'begin': event.begin.to('utc'),  # Convert to UTC or any desired timezone
            'end': event.end.to('utc'),
            'description': event.description,
            'location': event.location
        })

    # Convert to DataFrame
    df = pd.DataFrame(events)

    # Show the DataFrame
    print(df)
