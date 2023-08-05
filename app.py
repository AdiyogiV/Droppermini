import math
from flask import Flask, render_template, request, jsonify, abort
import os
from werkzeug.utils import secure_filename
import time
from flask import send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def formatFileSize(bytes):
    if bytes == 0:
        return '0 Bytes'
    k = 1024
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    i = int(math.floor(math.log(bytes) / math.log(k)))
    return f"{round(bytes / pow(k, i), 2)} {sizes[i]}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request.'}), 400
    file = request.files['file']
    # If user does not select file, return an error
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400
    if file and allowed_file(file.filename):
        # Ensure the 'uploads' directory exists before saving the file
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the file with the sanitized filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Get file details (size and timestamp)
        file_size = os.path.getsize(file_path)
        file_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))

        return jsonify({
            'message': 'File uploaded successfully!',
            'name': filename,
            'size': formatFileSize(file_size),
            'timestamp': file_timestamp
        }), 201
    else:
        return jsonify({'error': 'Invalid file format. Allowed file types: txt, pdf, png, jpg, jpeg, gif'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    files = []
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        return jsonify(files)
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_size = os.path.getsize(file_path)
        file_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
        files.append({
            'name': filename,
            'size': formatFileSize(file_size),
            'timestamp': file_timestamp
        })
    return jsonify(files), 200

if __name__ == '__main__':
    app.run(debug=True)
