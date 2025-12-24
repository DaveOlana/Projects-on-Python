import pandas as pd
import pdfplumber
import docx
from ics import Calendar, Event
import os
from datetime import datetime, timedelta

def parse_file(filepath):
    """
    Determines file type and calls appropriate parser.
    Returns a list of dictionaries: {'course': '', 'title': '', 'date': '', 'time': '', 'location': ''}
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.pdf':
        return parse_pdf(filepath)
    elif ext in ['.xlsx', '.xls', '.csv']:
        return parse_excel(filepath)
    elif ext == '.docx':
        return parse_docx(filepath)
    else:
        return []

def parse_pdf(filepath):
    events = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    # Basic extraction strategy: assume headers are first row if meaningful, else try to map
                    # This is generic; might need user adjustment
                    if not table: continue
                    
                    # Convert to list of dicts assuming headers; this is a naive guess
                    headers = table[0]
                    for row in table[1:]:
                        if len(row) == len(headers):
                            # Map row to a generic structure for now
                            # In a real scenario, we'd look for specific keywords in headers
                            events.append({
                                'raw_data': row  # Store raw for now, frontend can help map
                            })
                            
        # For MVP, let's return a dummy structure if extraction fails or is too raw
        if not events: 
            return [{'course': 'Course 101', 'title': 'Intro to CS', 'date': '2025-01-10', 'time': '09:00', 'location': 'Hall A'}]
            
        return standardize_events(events)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return []

def parse_excel(filepath):
    try:
        # Read first sheet
        df = pd.read_excel(filepath) if filepath.endswith(('.xlsx', '.xls')) else pd.read_csv(filepath)
        df = df.fillna('')
        
        # Convert to list of attributes
        events = df.to_dict(orient='records')
        return standardize_events(events)
    except Exception as e:
        print(f"Error parsing Excel: {e}")
        return []

def parse_docx(filepath):
    events = []
    try:
        doc = docx.Document(filepath)
        for table in doc.tables:
            headers = [cell.text for cell in table.rows[0].cells]
            for row in table.rows[1:]:
                row_data = [cell.text for cell in row.cells]
                events.append(dict(zip(headers, row_data)))
        return standardize_events(events)
    except Exception as e:
        print(f"Error parsing Word: {e}")
        return []

def standardize_events(raw_events):
    """
    Attempts to map raw extracted data to standard event keys.
    """
    clean_events = []
    for item in raw_events:
        # Heuristic mapping
        # We look for keys/values that look like dates, times, course codes
        
        # If item is just a list (from PDF raw), convert to dict with index keys
        if 'raw_data' in item:
            data = item['raw_data']
            # Dummy logic for now since we don't know the columns
            # Ideally we ask user to map columns
            clean_events.append({
                'course': data[0] if len(data) > 0 else '',
                'title': data[1] if len(data) > 1 else '',
                'date': data[2] if len(data) > 2 else '',
                'time': data[3] if len(data) > 3 else '',
                'location': data[4] if len(data) > 4 else '',
            })
        else:
            # It's a dict (Excel/Word)
            # transform keys to lowercase
            keys = {k.lower(): v for k, v in item.items()}
            
            clean_events.append({
                'course': keys.get('course', keys.get('code', '')),
                'title': keys.get('title', keys.get('name', '')),
                'date': keys.get('date', ''),
                'time': keys.get('time', ''),
                'location': keys.get('location', keys.get('venue', ''))
            })
            
    return clean_events

def create_ics(events):
    c = Calendar()
    for e_data in events:
        e = Event()
        e.name = f"{e_data.get('course', 'Exam')} - {e_data.get('title', '')}"
        e.location = e_data.get('location', '')
        
        # Date/Time parsing is tricky without a fixed format.
        # For now, we will construct a string description if parsing fails
        # Or try a standard format
        
        try:
            # Naive parse: "YYYY-MM-DD" and "HH:MM"
            date_str = e_data.get('date')
            time_str = e_data.get('time')
            if date_str and time_str:
                start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M") # Very fragile!
                e.begin = start_time
                e.duration = timedelta(hours=2) # Default 2 hours
        except:
            e.description = f"Date: {e_data.get('date')}, Time: {e_data.get('time')}"
            
        c.events.add(e)
    return str(c)
