from flask import Flask, jsonify, request, send_from_directory
import base64
import numpy as np
import cv2
from attentiveness_monitor import ClassroomMonitor
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

monitor = ClassroomMonitor()
REPORT_DIRECTORY = os.path.abspath("attentiveness_reports")
os.makedirs(REPORT_DIRECTORY, exist_ok=True)
print(f"Reports will be served from: {REPORT_DIRECTORY}")

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.get_json()
        student_id = data['student_id']
        image_data = data['image'].split(',')[1]
        decoded_data = base64.b64decode(image_data)
        nparr = np.frombuffer(decoded_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        analysis_result = monitor.analyze_student_frame(student_id, frame)
        return jsonify(student_id=student_id, result=analysis_result)
    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify(error=str(e)), 500

@app.route('/end_session', methods=['POST'])
def end_session():
    try:
        report_files = monitor.generate_all_reports()
        monitor.reset()
        return jsonify(status="success", reports=report_files)
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

@app.route('/download_report/<filename>', methods=['GET'])
def download_report(filename):
    try:
        return send_from_directory(directory=REPORT_DIRECTORY, path=filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify(error="File not found."), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)