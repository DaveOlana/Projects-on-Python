import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

from utils import parse_file_raw, apply_mapping_and_filter, create_ics

# ... (imports remain)

@app.route('/parse', methods=['POST'])
def parse_file_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = parse_file_raw(filepath)
        
        return jsonify({'message': 'File uploaded', 'filename': filename, 'raw_rows': result.get('rows', [])})

@app.route('/process_mapping', methods=['POST'])
def process_mapping_route():
    """
    Takes raw rows, column mapping indices, and filters.
    Returns the cleaned events list for preview.
    """
    data = request.json
    raw_rows = data.get('raw_rows', [])
    mapping = data.get('mapping', {})
    filters = data.get('filters', '')
    
    events = apply_mapping_and_filter(raw_rows, mapping, filters)
    return jsonify({'events': events})

@app.route('/generate_ics', methods=['POST'])
def generate_ics_route():
    data = request.json
    events = data.get('events', [])
    
    if not events:
        return jsonify({'error': 'No events to export'}), 400
        
    ics_content = create_ics(events)
    
    # Save generic ics file
    ics_filename = 'exam_timetable.ics'
    ics_path = os.path.join(app.config['UPLOAD_FOLDER'], ics_filename)
    
    with open(ics_path, 'w') as f:
        f.write(ics_content)
        
    return send_file(ics_path, as_attachment=True, download_name=ics_filename)

if __name__ == '__main__':
    app.run(debug=True)
