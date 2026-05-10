from flask import Flask, request, jsonify, send_from_directory, abort  
from flask_cors import CORS
 
import os
import database

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = '/home/yonatan/Bdoc'
app.config['MAX_CONTENT_LENGTH'] = 10*1024*1024

db = database.initdb()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        file_name = os.path.splitext(file.filename)[0]
        job_id = db.create_job(file_name, "hi", f"{app.config['UPLOAD_FOLDER']}/{file.filename}")
        return jsonify({"message": "File uploaded", "job_id": job_id}), 200

@app.route('/getepub', methods=['POST'])
def job_result():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
        
    job_id = data.get('job_id')
    if not job_id:
        return jsonify({"error": "No job_id provided"}), 400
        
    job_status = database.check_status(job_id)
    
    if job_status == "PENDING" or job_status == "PROCESSING":
        print(f"Pending for {job_id} status is {job_status}")
        return jsonify({"status": job_status, "message": f"Job is {job_status.lower()}"}), 202
    elif job_status == "COMPLETED":
        print(f"Job is complete {job_id}")
        full_path = database.get_epub_path(job_id)
        epub_name = database.get_epub_name(job_id)
        
        if not full_path or not os.path.exists(full_path):
            print(f"Error no file found {full_path}")
            return jsonify({"error": "EPUB file not found"}), 404
            
        directory_path = os.path.dirname(full_path)
        file_name = os.path.basename(full_path)

        print(f"Sending file: {full_path}")
        print(f"Directory: {directory_path}")
        print(f"Filename: {file_name}")
        print(f"Download name: {epub_name}")
        
        return send_from_directory(
            directory_path, 
            file_name, 
            as_attachment=True, 
            download_name=f"converted_{epub_name}.epub"
        )
    else:
        print(f"No job found {job_id}")
        return jsonify({"error": "Job not found"}), 404

if __name__=="__main__":
    app.run(port=5000, debug=True) 
