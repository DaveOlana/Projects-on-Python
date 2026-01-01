from flask import Flask, render_template, request, jsonify, send_file
from utils import parse_natural_language, create_ics
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'exports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# Ensure export directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/parse_nl', methods=['POST'])
def parse_natural_language_route():
    """
    Parse natural language input and return structured event data.
    
    Request body:
        {
            "input": "Monday 10am Team Meeting for 2 hours"
        }
    
    Response:
        {
            "success": true,
            "event": {
                "title": "Team Meeting",
                "date": "2025-01-06",
                "startTime": "10:00",
                "endTime": "12:00",
                "duration": 120
            }
        }
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
            'duration': result['duration']
        }
    })

@app.route('/generate_ics', methods=['POST'])
def generate_ics_route():
    """
    Generate ICS file from event list.
    
    Request body:
        {
            "events": [
                {
                    "title": "Team Meeting",
                    "date": "2025-01-15",
                    "startTime": "10:00",
                    "endTime": "11:00",
                    "priority": "yellow",
                    "notes": ""
                }
            ]
        }
    
    Response:
        ICS file download
    """
    data = request.json
    events = data.get('events', [])
    
    if not events:
        return jsonify({'error': 'No events to export'}), 400
    
    try:
        ics_content = create_ics(events)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ics_filename = f'calendme_schedule_{timestamp}.ics'
        ics_path = os.path.join(app.config['UPLOAD_FOLDER'], ics_filename)
        
        # Write ICS file
        with open(ics_path, 'w', encoding='utf-8') as f:
            f.write(ics_content)
        
        return send_file(ics_path, as_attachment=True, download_name=ics_filename)
    
    except Exception as e:
        return jsonify({'error': f'Failed to generate ICS: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
