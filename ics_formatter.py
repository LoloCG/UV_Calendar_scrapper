import pandas as pd
from ics import Calendar
import json

def main_ics_formater():
    convert_schedule_json_to_df()

def convert_schedule_json_to_df():
    '''
        Example output in original schedule json:
            "tipo_franja": "ALU",
            "periodo_academico": "2024-25",
            "inicio": "2024-09-16T08:00:00Z",
            "fin": "2024-09-16T09:00:00Z",
            "descripcion_periodo": " ",
            "nombre_lugar": "AULA AF-14 B",
            "identificador_edificio": "21",
            "capacidad_aula": null,
            "capacidad_examen_aula": null,
            "codigo_asignatura": 34082,
            "identificador_asignatura": "      000034082",
            "aula_virtual_link": null,
            "nombre_asignatura": "TECNOLOGÍA FARMACEUTICA I",
            "codigo_actividad": 7061,
            "nombre_actividad": "Teoría (34082)",
            "codigo_grupo": 41210,
            "identificador_grupo": "DG-T",
            "nombre_grupo": "Grupo teoría",
            "profesores": [...]
        categories required:
            inicio
            fin
            nombre_lugar
            codigo_asignatura
            nombre_asignatura
            nombre_actividad
            identificador_grupo
            nombre_grupo
    '''
    with open('schedule.json', 'r', encoding='utf-8') as f:
        data = json.load(f)  
    
    items = data.get('items', [])  

    df = pd.json_normalize(items)

    wanted_columns = ['inicio', 'fin', 'nombre_lugar', 'codigo_asignatura', 'nombre_asignatura', 'nombre_actividad', 'identificador_grupo']
    df = df[wanted_columns]
    
    print(df.columns.tolist())
    print()
    print(df.head())

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
        categories required:

    '''
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
    print(df.head())
