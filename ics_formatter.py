"""
    For each event:
    - `BEGIN:VEVENT` / `END:VEVENT`: Marks the start and end of each event in the calendar.
    - UID: A globally unique identifier for the event (used for synchronization across calendars).
    - DTSTAMP: The date and time the event was created or last modified, usually in UTC.
    - DTSTART: The start date and time of the event, in UTC or local time with a time zone.
    - DTEND
    - SUMMARY
    - DESCRIPTION
    - LOCATION
    - PRIORITY
"""

import pandas as pd
from ics import Calendar
import json
from datetime import datetime

def main_ics_formater():
    schedule_df = convert_schedule_json_to_df()
    # schedule_df.to_csv('schedule.csv', index=False, sep=';',header=True)

    events_df = convert_event_cal_ics_to_df()
    # events_df.to_csv('events.csv', index=False, sep=';',header=True)

    combined_df = join_both_df(schedule_df, events_df)

def convert_schedule_json_to_df():
    '''
        final columns: ['asignatura', 'actividad', 'grupo', 'DTSTART', 'DTEND', 'lugar']
    '''
    def convert_dates_to_ics_standard(df):
        df['DTSTART'] = pd.to_datetime(df['inicio'], utc=True)
        df['DTSTART'] = df['DTSTART'].dt.strftime('%Y%m%dT%H%M%SZ')

        df['DTEND'] = pd.to_datetime(df['fin'], utc=True)
        df['DTEND'] = df['DTEND'].dt.strftime('%Y%m%dT%H%M%SZ')

        df.drop('inicio', axis=1,inplace=True)
        df.drop('fin', axis=1,inplace=True)

        return df

    def set_priorities_by_act(row):
        actividad = row['actividad']
        priority = None
        
        if 'Seminario' in actividad:
            priority = int(4)
        elif 'Laboratorio' in actividad:
            priority = int(2)
        elif 'Teoría' in actividad:
            priority = int(7)

        return priority

    def add_sem_and_lab_to_summary(row):
        actividad = row['actividad']
        summary = row['SUMMARY']

        if 'Seminario' in actividad:
            summary = 'Seminario ' + summary
        elif 'Laboratorio' in actividad:
            summary = 'Laboratorio ' + summary
    
        return summary

    def obtain_df_from_json():
        with open('schedule.json', 'r', encoding='utf-8') as f:
            data = json.load(f)  
        
        items = data.get('items', [])  

        df = pd.json_normalize(items)
        return df
    
    df = obtain_df_from_json()

    wanted_columns = ['inicio', 'fin', 'nombre_lugar', 'nombre_asignatura', 'nombre_actividad', 'identificador_grupo','identificador_edificio'] # , 'codigo_asignatura'
    df = df[wanted_columns]
    
    df = convert_dates_to_ics_standard(df)

    df.rename(columns={
        'nombre_actividad': 'actividad',
        'nombre_asignatura': 'SUMMARY',
        'identificador_grupo': 'grupo',
        }, inplace=True)

    df['actividad'] = df['actividad'].str.split(' ').str[0]
    df['actividad'] = df['actividad'].str.capitalize()
    df['SUMMARY'] = df['SUMMARY'].str.capitalize()
    
    df['nombre_lugar'] = df['nombre_lugar'].str.replace("AULA","Class")
    df['LOCATION'] = df['nombre_lugar'].str.cat(df['identificador_edificio'], sep=' Building ',na_rep='')
    df.drop('identificador_edificio', axis=1,inplace=True)
    df.drop('nombre_lugar', axis=1,inplace=True)

    df['DESCRIPTION'] = df['actividad'].str.cat(df['grupo'], sep='. ', na_rep='')    
    df.drop('grupo', axis=1,inplace=True)
    
    current_time = datetime.utcnow()
    df['DTSTAMP'] = current_time.strftime('%Y%m%dT%H%M%SZ')

    df['PRIORITY'] = df.apply(set_priorities_by_act, axis=1)

    df['SUMMARY'] = df.apply(add_sem_and_lab_to_summary, axis=1)
    df.drop('actividad', axis=1,inplace=True)

    return df

def convert_event_cal_ics_to_df():
    ''' 
        Example output in original event calendar ics:
            BEGIN:VCALENDAR
            METHOD:PUBLISH
            PRODID:-//Moodle Pty Ltd//NONSGML Moodle Version 2022112809.02//EN
            VERSION:2.0
            
            BEGIN:VEVENT
            UID:8314693@aulavirtual.uv.es
            SUMMARY:Asistencia S1 s'obre el
            DESCRIPTION:
            CLASS:PUBLIC
            LAST-MODIFIED:20240909T141113Z
            DTSTAMP:20240918T062706Z
            DTSTART:20240925T092000Z
            DTEND:20240925T092000Z
            CATEGORIES:2024-25 Gestió i planificació farmacèutiques Gr.DG-T (34072)
            END:VEVENT

        columns to process: description, dtstamp
        final columns: ['short_descript', 'last_modified', 'DTSTART', 'DTEND', 'actividad','asignatura']
        columns to achieve: ['asignatura', 'actividad', 'grupo', 'DTSTART', 'DTEND', 'lugar']
    '''
    def categorize_activity(short_descript):
        exercises_keywords = ['cuestionario','questionario','quiz','tarea','evaluación continua']
        exam_keywords = ['exam','test','examen']
        obligatory_presence_keywords = ['asistencia', 'tutoría', 'seminario']

        if any(keyword in short_descript.lower() for keyword in exercises_keywords):
            return 'Exercises'
        elif any(keyword in short_descript.lower() for keyword in exam_keywords):
            return 'Exam'
        elif any(keyword in short_descript.lower() for keyword in obligatory_presence_keywords):
            return 'Obligatory class'
        else:
            return 'event'
 
    ics_file_path = 'event_calendar.ics'
    with open(ics_file_path, 'r',encoding='utf-8') as f:
        calendar = Calendar(f.read())

    events = []
    for event in calendar.events:
        categories_str = event.categories if isinstance(event.categories, str) else ', '.join(event.categories)
        description_str = event.description if isinstance(event.description, str) else ' '.join(event.description)

        events.append({
            'short_descript': event.name,
            # 'class': event.classification,
            'asignatura': categories_str,
            # 'dtstamp': event.created.datetime,
            'DTSTAMP': event.last_modified.datetime,
            'DTSTART': event.begin.datetime,
            'DTEND': event.end.datetime,
            'description': description_str,
        })

    df = pd.DataFrame(events)

    df['DTSTART'] = pd.to_datetime(df['DTSTART'], utc=True).dt.strftime('%Y%m%dT%H%M%SZ')
    df['DTEND'] = pd.to_datetime(df['DTEND'], utc=True).dt.strftime('%Y%m%dT%H%M%SZ')
    # df['dtstamp'] = pd.to_datetime(df['dtstamp'], utc=True).dt.strftime('%Y%m%dT%H%M%SZ')
    df['DTSTAMP'] = pd.to_datetime(df['DTSTAMP'], utc=True).dt.strftime('%Y%m%dT%H%M%SZ')

    df['asignatura'] = df['asignatura'].str[8:]
    df['asignatura'] = df['asignatura'].str[0:-8]


    df['SUMMARY'] = df['short_descript'].apply(categorize_activity)

    df['DESCRIPTION'] = df['asignatura'].str.cat(df['short_descript'], sep='. ', na_rep='')
    df['DESCRIPTION'] = df['DESCRIPTION'].str.cat(df['description'], sep='. ', na_rep='')

    df.drop('asignatura', axis=1, inplace=True) 
    df.drop('short_descript', axis=1, inplace=True) 
    df.drop('description', axis=1, inplace=True) 
    
    return df

def join_both_df(schedule_df, events_df):
    df = pd.concat([schedule_df, events_df], axis=0)
    df.to_csv('events.csv', index=False, sep=';', header=True)

    return df


