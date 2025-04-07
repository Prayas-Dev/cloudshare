from flask import Flask, render_template, request, redirect, send_from_directory, send_file, url_for
import os
from datetime import datetime
from zipfile import ZipFile
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        size_kb = round(os.path.getsize(filepath) / 1024, 2)
        upload_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
        files.append({
            'name': filename,
            'size': size_kb,
            'upload_time': upload_time,
            'ext': os.path.splitext(filename)[1][1:].lower()
        })
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return redirect('/')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect('/')

@app.route('/download-zip', methods=['POST'])
def download_zip():
    files = request.form.getlist('files')
    zip_stream = io.BytesIO()
    with ZipFile(zip_stream, 'w') as zf:
        for f in files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f)
            if os.path.exists(filepath):
                zf.write(filepath, arcname=f)
    zip_stream.seek(0)
    return send_file(zip_stream, mimetype='application/zip', as_attachment=True, download_name='files.zip')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
