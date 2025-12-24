import pandas as pd
import pdfplumber
import docx
from ics import Calendar, Event
import os
from datetime import datetime, timedelta

def parse_file_raw(filepath):
    """
    Extracts raw tabular data from the file.
    Returns: A list of dicts, where each dict represents a sheet/page with 'name' and 'rows' (list of lists).
    For now, we merge all found tables into one big list of rows for simplicity,
    or return the first substantial table found.
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.pdf':
        return parse_pdf_raw(filepath)
    elif ext in ['.xlsx', '.xls', '.csv']:
        return parse_excel_raw(filepath)
    elif ext == '.docx':
        return parse_docx_raw(filepath)
    else:
        return {'error': 'Unsupported file type'}

def parse_pdf_raw(filepath):
    all_rows = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        # cleanup: remove empty rows or rows that are just all None
                        for row in table:
                            if any(cell and cell.strip() for cell in row):
                                all_rows.append([cell.strip() if cell else "" for cell in row])
        return {'rows': all_rows}
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return {'rows': []}

def parse_excel_raw(filepath):
    try:
        # Read with header=None to get raw rows including headers
        df = pd.read_excel(filepath, header=None) if filepath.endswith(('.xlsx', '.xls')) else pd.read_csv(filepath, header=None)
        df = df.fillna('')
        # Convert to list of lists
        rows = df.values.tolist()
        # Convert all to string for consistency
        rows = [[str(cell).strip() for cell in row] for row in rows]
        return {'rows': rows}
    except Exception as e:
        print(f"Error parsing Excel: {e}")
        return {'rows': []}

def parse_docx_raw(filepath):
    all_rows = []
    try:
        doc = docx.Document(filepath)
        for table in doc.tables:
            for row in table.rows:
                cell_data = [cell.text.strip() for cell in row.cells]
                if any(cell_data):
                    all_rows.append(cell_data)
        return {'rows': all_rows}
    except Exception as e:
        print(f"Error parsing Word: {e}")
        return {'rows': []}

def apply_mapping_and_filter(raw_rows, mapping, filters):
    """
    Transforms raw rows into structured events based on user mapping.
    
    Args:
        raw_rows (list): List of lists containing the table data.
        mapping (dict): {'course': col_idx, 'date': col_idx, 'time': col_idx, ...}
                        Indices can be string 'null' if not mapped.
        filters (str): Comma-separated string of keywords to keep. Empty means keep all.
    """
    events = []
    
    # helper: safely get index or None
    def get_val(row, idx_key):
        idx = mapping.get(idx_key)
        if idx is not None and isinstance(idx, int) and 0 <= idx < len(row):
            return row[idx]
        return ""

    filter_keywords = [f.strip().lower() for f in filters.split(',')] if filters else []

    for row in raw_rows:
        # 1. Extraction
        course = get_val(row, 'course')
        title = get_val(row, 'title')
        date_str = get_val(row, 'date')
        time_str = get_val(row, 'time')
        location = get_val(row, 'location')

        # Simple validation: Must have at least a course code or title to be valid
        if not course and not title:
            continue

        # 2. Filtering
        # If filters exist, check if ANY of the mapped fields contain ANY of the keywords
        if filter_keywords:
            row_text = " ".join([str(c).lower() for c in [course, title, location]]).lower()
            if not any(k in row_text for k in filter_keywords):
                continue
        
        events.append({
            'course': course,
            'title': title,
            'date': date_str,
            'time': time_str,
            'location': location
        })

    return events

def create_ics(events):
    c = Calendar()
    for e_data in events:
        e = Event()
        e.name = f"{e_data.get('course', '')} - {e_data.get('title', '')}".strip(" -")
        e.location = e_data.get('location', '')
        
        # Improved Date/Time parsing attempt
        date_str = e_data.get('date', '').strip()
        time_str = e_data.get('time', '').strip()
        
        # Try to combine and parse standard ISO-ish formats
        # Real-world parsing is header, we might need a robust library like dateutil or custom logic later
        # For now, just dump description if fail
        timestamp = None
        
        try:
            # Try combining provided date and time
            # Common formats: "YYYY-MM-DD" + "HH:MM"
            full_str = f"{date_str} {time_str}".strip()
            # formatting attempts
            formats = [
                "%Y-%m-%d %H:%M", "%d-%m-%Y %H:%M", "%m/%d/%Y %H:%M", 
                "%Y/%m/%d %H:%M", "%d/%m/%Y %H:%M",
                "%Y-%m-%d %I:%M %p" # 12 hour format
            ]
            
            for fmt in formats:
                try:
                    timestamp = datetime.strptime(full_str, fmt)
                    break
                except ValueError:
                    continue
            
            if timestamp:
                e.begin = timestamp
                e.duration = timedelta(hours=2) # Default duration
            else:
                 # Fallback to pure Description if we can't parse
                 e.description = f"Date: {date_str}\nTime: {time_str}"
                 # Required for ICS validity if start is missing? 
                 # ICS usually requires a start time. Let's make it an all-day event on Today if fail?
                 # Better: just set description and don't set begin (might be invalid event)
                 # Reverting to putting info in description
                 pass

        except Exception as err:
            print(f"Date Parse Error: {err}")
            e.description = f"Date: {date_str}\nTime: {time_str}"

        c.events.add(e)
    return str(c)
