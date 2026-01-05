from flask import Flask, render_template, request, jsonify, send_file
from utils import parse_natural_language, create_ics
import os
import json
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['TEMP_FOLDER'] = 'exports/temp'
app.config['PERMANENT_FOLDER'] = 'exports/permanent'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# Ensure export directories exist
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
os.makedirs(app.config['PERMANENT_FOLDER'], exist_ok=True)

def cleanup_old_files():
    """
    Lazy cleanup: Delete temp files older than 6 hours.
    Runs on server startup and before each new file generation.
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=6)
        
        for filename in os.listdir(app.config['TEMP_FOLDER']):
            filepath = os.path.join(app.config['TEMP_FOLDER'], filename)
            
            # Check file modification time
            if os.path.isfile(filepath):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_mtime < cutoff_time:
                    os.remove(filepath)
                    print(f"Cleaned up old temp file: {filename}")
    except Exception as e:
        print(f"Cleanup error: {e}")

def get_event_hash(events):
    """
    Generate unique hash for events list to detect duplicates.
    """
    events_str = json.dumps(events, sort_keys=True)
    return hashlib.md5(events_str.encode()).hexdigest()[:8]

def find_duplicate_temp_file(event_hash):
    """
    Check if a temp file with same event hash already exists.
    Returns filename if found, None otherwise.
    """
    try:
        for filename in os.listdir(app.config['TEMP_FOLDER']):
            if event_hash in filename:
                filepath = os.path.join(app.config['TEMP_FOLDER'], filename)
                # Check if file is still valid (< 6 hours old)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if datetime.now() - file_mtime < timedelta(hours=6):
                    return filename
    except Exception as e:
        print(f"Duplicate check error: {e}")
    return None

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for online/offline detection.
    Returns detailed status information.
    """
    return jsonify({
        'status': 'ok',
        'online': True,
        'timestamp': datetime.now().isoformat(),
        'server': 'CalendME',
        'version': '1.0.0'
    })

@app.route('/parse_nl', methods=['POST'])
def parse_natural_language_route():
    """
    Parse natural language input and return structured event data.
    """
    data = request.json
    input_text = data.get('input', '')
    
    if not input_text:
        return jsonify({'success': False, 'error': 'No input provided'}), 400
    
    result = parse_natural_language(input_text)
    
    if result.get('error'):
        return jsonify({'success': False, 'error': result['error']}), 400
    
    return jsonify({
        'success': True,
        'event': {
            'title': result['title'],
            'date': result['date'],
            'startTime': result['startTime'],
            'endTime': result['endTime'],
            'duration': result['duration'],
            'reminder': result.get('reminder')
        }
    })

@app.route('/generate_ics', methods=['POST'])
def generate_ics_route():
    """
    Generate ICS file for calendar export.
    Supports both WebCal (temp) and Download (permanent) modes.
    
    Request body:
        {
            "events": [...],
            "mode": "webcal" | "download",
            "filename": "My Schedule" (optional, for download mode)
        }
    """
    data = request.json
    events = data.get('events', [])
    mode = data.get('mode', 'download')  # Default to download
    custom_filename = data.get('filename', '')
    
    if not events:
        return jsonify({'error': 'No events to export'}), 400
    
    try:
        # Run cleanup before generating new file
        cleanup_old_files()
        
        # Generate ICS content
        ics_content = create_ics(events)
        
        if mode == 'webcal':
            # WebCal mode: Create temp file for one-click add
            event_hash = get_event_hash(events)
            
            # Check for duplicate
            existing_file = find_duplicate_temp_file(event_hash)
            if existing_file:
                # Reuse existing file
                webcal_url = f"webcal://{request.host}/temp/{existing_file}"
                return jsonify({
                    'success': True,
                    'mode': 'webcal',
                    'url': webcal_url,
                    'filename': existing_file,
                    'duplicate': True
                })
            
            # Create new temp file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_filename = f'calendme_{timestamp}_{event_hash}.ics'
            temp_path = os.path.join(app.config['TEMP_FOLDER'], temp_filename)
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(ics_content)
            
            # Generate WebCal URL
            webcal_url = f"webcal://{request.host}/temp/{temp_filename}"
            
            return jsonify({
                'success': True,
                'mode': 'webcal',
                'url': webcal_url,
                'filename': temp_filename,
                'duplicate': False
            })
        
        else:
            # Download mode: Create permanent file with custom name
            if custom_filename:
                # Sanitize filename
                safe_filename = "".join(c for c in custom_filename if c.isalnum() or c in (' ', '-', '_')).strip()
                if not safe_filename:
                    safe_filename = 'schedule'
                perm_filename = f'{safe_filename}.ics'
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                perm_filename = f'calendme_schedule_{timestamp}.ics'
            
            perm_path = os.path.join(app.config['PERMANENT_FOLDER'], perm_filename)
            
            with open(perm_path, 'w', encoding='utf-8') as f:
                f.write(ics_content)
            
            return send_file(perm_path, as_attachment=True, download_name=perm_filename)
    
    except Exception as e:
        return jsonify({'error': f'Failed to generate ICS: {str(e)}'}), 500

@app.route('/temp/<filename>')
def serve_temp_file(filename):
    """
    Serve temporary ICS files for WebCal protocol.
    """
    try:
        filepath = os.path.join(app.config['TEMP_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, mimetype='text/calendar', as_attachment=False)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run cleanup on server startup
cleanup_old_files()

if __name__ == '__main__':
    app.run(debug=True)
