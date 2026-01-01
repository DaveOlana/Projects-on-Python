import re
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
import dateparser
import parsedatetime
from ics import Calendar, Event

# Initialize parsedatetime calendar for relative date parsing
cal = parsedatetime.Calendar()

def parse_natural_language(input_text):
    """
    Parse natural language input into structured event data.
    
    Handles patterns like:
    - "Monday 10am Team Meeting"
    - "4th of January, study for 4 hours (6am to 10am)"
    - "Jan 15 3pm Football for 2 hours"
    - "Four days from now, study from 6am to 11am"
    - "Tomorrow 9:30am Dentist appointment"
    - "Next Friday 2pm Project review. Reminder 30 min before"
    
    Returns:
        dict: {
            'title': str,
            'date': str (ISO format YYYY-MM-DD),
            'startTime': str (HH:MM format),
            'duration': int (minutes),
            'endTime': str (HH:MM format),
            'reminder': int (minutes before) or None,
            'error': None or str
        }
    """
    result = {
        'title': '',
        'date': '',
        'startTime': '',
        'duration': None,
        'endTime': '',
        'reminder': None,
        'error': None
    }
    
    try:
        original_input = input_text
        cleaned_input = input_text.lower()
        
        # Extract reminder first
        reminder_patterns = [
            r'remind(?:er)?\s+(\d+)\s*(?:min(?:ute)?s?|hrs?|hours?)\s+before',
            r'(\d+)\s*(?:min(?:ute)?s?|hrs?|hours?)\s+(?:before|reminder)',
            r'set\s+(?:a\s+)?reminder\s+(\d+)\s*(?:min(?:ute)?s?|hrs?|hours?)',
        ]
        
        for pattern in reminder_patterns:
            match = re.search(pattern, cleaned_input)
            if match:
                value = int(match.group(1))
                if 'hour' in pattern or 'hr' in pattern:
                    result['reminder'] = value * 60
                else:
                    result['reminder'] = value
                # Remove reminder from input for cleaner parsing
                input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE).strip()
                cleaned_input = input_text.lower()
                break
        
        # Extract explicit time ranges: "from 6am to 10am" or "6am to 10am" or "6am-10am"
        start_time = None
        end_time = None
        
        time_range_patterns = [
            r'from\s+(\d{1,2}(?::\d{2})?)\s*([ap]m?)\s+to\s+(\d{1,2}(?::\d{2})?)\s*([ap]m?)',
            r'(\d{1,2}(?::\d{2})?)\s*([ap]m?)\s+to\s+(\d{1,2}(?::\d{2})?)\s*([ap]m?)',
            r'(\d{1,2}(?::\d{2})?)\s*([ap]m?)\s*-\s*(\d{1,2}(?::\d{2})?)\s*([ap]m?)',
            r'\((\d{1,2}(?::\d{2})?)\s*([ap]m?)\s+to\s+(\d{1,2}(?::\d{2})?)\s*([ap]m?)\)',
        ]
        
        for pattern in time_range_patterns:
            match = re.search(pattern, cleaned_input)
            if match:
                start_hour = match.group(1)
                start_meridiem = match.group(2)
                end_hour = match.group(3)
                end_meridiem = match.group(4)
                
                start_time = parse_time_string(start_hour, start_meridiem)
                end_time = parse_time_string(end_hour, end_meridiem)
                
                # Remove time range from input
                input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE).strip()
                cleaned_input = input_text.lower()
                break
        
        # If no explicit range, extract duration: "for 2 hours" or "for 90 minutes"
        duration_minutes = None
        if not end_time:
            duration_patterns = [
                r'for\s+(\d+)\s*hours?',
                r'for\s+(\d+)\s*hrs?',
                r'for\s+(\d+)\s*minutes?',
                r'for\s+(\d+)\s*mins?',
                r'for\s+(\d+)h',
                r'for\s+(\d+)m',
                r'(\d+)\s*hour\s+(?:meeting|session|event)',
                r'(\d+)\s*min\s+(?:call|meeting)',
            ]
            
            for pattern in duration_patterns:
                match = re.search(pattern, cleaned_input)
                if match:
                    value = int(match.group(1))
                    if 'hour' in pattern or 'hr' in pattern or 'h' in pattern:
                        duration_minutes = value * 60
                    else:
                        duration_minutes = value
                    # Remove duration from text
                    input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE).strip()
                    cleaned_input = input_text.lower()
                    break
        
        # Try to extract explicit date: "4th of January", "January 4th", "Jan 4"
        explicit_date = None
        date_patterns = [
            r'(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})(?:st|nd|rd|th)?',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, cleaned_input)
            if match:
                if pattern.startswith(r'(\d'):  # "4th of January"
                    day = int(match.group(1))
                    month_str = match.group(2)
                else:  # "January 4th"
                    month_str = match.group(1)
                    day = int(match.group(2))
                
                # Get current year or next year if date has passed
                current_date = datetime.now()
                month_map = {
                    'january': 1, 'february': 2, 'march': 3, 'april': 4,
                    'may': 5, 'june': 6, 'july': 7, 'august': 8,
                    'september': 9, 'october': 10, 'november': 11, 'december': 12,
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                    'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9,
                    'oct': 10, 'nov': 11, 'dec': 12
                }
                month = month_map.get(month_str.lower())
                
                if month:
                    year = current_date.year
                    try:
                        explicit_date = datetime(year, month, day)
                        # If date is in the past, assume next year
                        if explicit_date < current_date:
                            explicit_date = datetime(year + 1, month, day)
                    except ValueError:
                        pass  # Invalid date, let other parsers handle it
                
                # Remove date from input
                input_text = re.sub(pattern, '', input_text, flags=re.IGNORECASE).strip()
                cleaned_input = input_text.lower()
                break
        
        # Use dateparser for smart date/time extraction
        parsed_dt = dateparser.parse(
            input_text,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now(),
                'RETURN_AS_TIMEZONE_AWARE': False,
                'PREFER_DAY_OF_MONTH': 'first'
            }
        )
        
        if not parsed_dt:
            # Fallback to parsedatetime
            time_struct, parse_status = cal.parse(input_text)
            if parse_status:
                parsed_dt = datetime(*time_struct[:6])
        
        # Use explicit date if found, otherwise use parsed date
        if explicit_date:
            final_date = explicit_date
            # If no time was extracted yet, use parsed_dt time or default to 9am
            if not start_time and parsed_dt:
                start_time = parsed_dt.strftime('%H:%M')
            elif not start_time:
                start_time = '09:00'
        elif parsed_dt:
            final_date = parsed_dt
            if not start_time:
                start_time = parsed_dt.strftime('%H:%M')
        else:
            result['error'] = 'Could not parse date/time. Try: "Monday 10am Meeting" or "4th of January 9am Study"'
            return result
        
        result['date'] = final_date.strftime('%Y-%m-%d')
        
        # Set start time
        if start_time:
            result['startTime'] = start_time
        else:
            result['startTime'] = final_date.strftime('%H:%M')
        
        # Calculate end time
        if end_time:
            result['endTime'] = end_time
            # Calculate duration from start to end
            start_dt = datetime.strptime(result['startTime'], '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            if end_dt < start_dt:  # End time next day
                end_dt += timedelta(days=1)
            result['duration'] = int((end_dt - start_dt).total_seconds() / 60)
        elif duration_minutes:
            result['duration'] = duration_minutes
            start_dt = datetime.strptime(result['startTime'], '%H:%M')
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            result['endTime'] = end_dt.strftime('%H:%M')
        else:
            # Default duration: 1 hour
            result['duration'] = 60
            start_dt = datetime.strptime(result['startTime'], '%H:%M')
            end_dt = start_dt + timedelta(hours=1)
            result['endTime'] = end_dt.strftime('%H:%M')
        
        # Extract title - clean up remaining text
        title = input_text
        
        # Remove common filler words and date/time remnants
        remove_words = [
            r'\btoday\b', r'\btomorrow\b', r'\bnext\b', r'\bthis\b', r'\blast\b',
            r'\bweek\b', r'\bmonth\b', r'\bdays?\b', r'\bfrom\b', r'\bnow\b',
            r'\bat\b', r'\bon\b', r'\bin\b', r'\bthe\b', r'\ba\b', r'\ban\b',
            r'\d{1,2}:\d{2}', r'\d{1,2}am', r'\d{1,2}pm',
            r',', r'\(', r'\)', r'\s+'
        ]
        
        for pattern in remove_words:
            title = re.sub(pattern, ' ', title, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        title = ' '.join(title.split())
        
        result['title'] = title.strip() if title.strip() else 'New Event'
                
    except Exception as e:
        result['error'] = f'Parsing error: {str(e)}'
    
    return result


def parse_time_string(time_str, meridiem):
    """
    Convert time string like "6" or "10:30" with "am"/"pm" to HH:MM format.
    """
    # Remove any extra chars
    time_str = time_str.strip()
    meridiem = meridiem.strip().lower()
    
    # Parse hour and minute
    if ':' in time_str:
        parts = time_str.split(':')
        hour = int(parts[0])
        minute = int(parts[1])
    else:
        hour = int(time_str)
        minute = 0
    
    # Convert to 24-hour format
    if meridiem.startswith('p') and hour != 12:
        hour += 12
    elif meridiem.startswith('a') and hour == 12:
        hour = 0
    
    return f'{hour:02d}:{minute:02d}'


def create_ics(events):
    """
    Create ICS calendar file from event list.
    
    Args:
        events (list): List of event dicts with structure:
            {
                'title': str,
                'date': str (YYYY-MM-DD),
                'startTime': str (HH:MM),
                'endTime': str (HH:MM),
                'priority': str ('red', 'yellow', 'green'),
                'notes': str (optional),
                'reminder': int (minutes before, optional)
            }
    
    Returns:
        str: ICS file content
    """
    c = Calendar()
    
    for event_data in events:
        e = Event()
        
        # Set event name/summary
        e.name = event_data.get('title', 'Untitled Event')
        
        # Parse date and time
        date_str = event_data.get('date', '')
        start_time_str = event_data.get('startTime', '')
        end_time_str = event_data.get('endTime', '')
        
        try:
            # Combine date and time
            start_dt_str = f"{date_str} {start_time_str}"
            start_dt = datetime.strptime(start_dt_str, '%Y-%m-%d %H:%M')
            e.begin = start_dt
            
            # Set end time
            if end_time_str:
                end_dt_str = f"{date_str} {end_time_str}"
                end_dt = datetime.strptime(end_dt_str, '%Y-%m-%d %H:%M')
                
                # Handle cases where end time is next day (e.g., 11pm to 1am)
                if end_dt <= start_dt:
                    end_dt += timedelta(days=1)
                    
                e.end = end_dt
            else:
                # Default to 1 hour duration
                e.end = start_dt + timedelta(hours=1)
        
        except Exception as err:
            print(f"Date parsing error for event '{e.name}': {err}")
            # Skip this event if date parsing fails
            continue
        
        # Add priority as category
        priority = event_data.get('priority', 'green')
        priority_labels = {
            'red': 'URGENT',
            'yellow': 'IMPORTANT',
            'green': 'NORMAL'
        }
        e.categories = [priority_labels.get(priority, 'NORMAL')]
        
        # Add description/notes
        notes = event_data.get('notes', '')
        if notes:
            e.description = notes
        
        # Add reminder/alarm (if supported)
        reminder_minutes = event_data.get('reminder')
        if reminder_minutes:
            # Note: python-ics 0.7.2 doesn't have built-in alarm support
            # We'll add it manually to description for now
            reminder_text = f"\n\n⏰ Reminder set for {reminder_minutes} minutes before event"
            e.description = (e.description or '') + reminder_text
        
        c.events.add(e)
    
    return str(c)
