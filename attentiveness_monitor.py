# ========================================================================================
#  Pro Attentiveness Monitor - Backend Logic (Version 15.0 - "The Unbreakable Build")
# ========================================================================================
#  - CRASH FIXED: Implements a threading.Lock to prevent the MediaPipe timestamp
#    mismatch error by ensuring only one image is processed at a time.
#  - ARCHITECTURE: The definitive Multi-Student, State-Managed Backend. Correctly
#    handles multiple, independent student trackers.
# ========================================================================================

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import os
import warnings
from threading import Lock # NEW: Import the lock for thread safety

warnings.filterwarnings('ignore')

class StudentTracker:
    # This class is correct from the previous working version and needs no changes.
    # Included here for a complete file.
    MIN_FRAMES_FOR_REPORT = 30 
    def __init__(self, student_id):
        self.id = student_id; self.name = f"Participant {student_id.split('-')[-1]}"
        self.EAR_THRESHOLD = 0.22; self.YAWN_THRESHOLD = 0.7; self.GAZE_THRESHOLD = 0.3
        self.drowsy_counter = 0; self.yawn_counter = 0; self.gaze_counter = 0
        self.raw_score = 75.0; self.smoothed_score = 75.0; self.SMOOTHING_ALPHA = 0.1
        self.attention_log = []; self.start_time = time.time()
        self.report_dir = "attentiveness_reports"; os.makedirs(self.report_dir, exist_ok=True)
    def update_score(self, new_raw_score):
        self.raw_score = new_raw_score
        self.smoothed_score = (self.SMOOTHING_ALPHA * self.raw_score) + ((1 - self.SMOOTHING_ALPHA) * self.smoothed_score)
    def _calculate_ear(self, eye_pts):
        v1 = np.linalg.norm(eye_pts[1] - eye_pts[5]); v2 = np.linalg.norm(eye_pts[2] - eye_pts[4])
        h = np.linalg.norm(eye_pts[0] - eye_pts[3])
        return (v1 + v2) / (2.0 * h) if h > 1e-6 else 0.0
    def _calculate_gaze_ratio(self, eye_pts, iris_center):
        try:
            eye_center_x = (eye_pts[0][0] + eye_pts[3][0]) / 2
            eye_width = np.linalg.norm(eye_pts[0] - eye_pts[3])
            return (iris_center[0] - eye_center_x) / eye_width if eye_width > 0 else 0.0
        except: return 0.0
    def analyze_face(self, face_landmarks, frame_shape):
        h, w = frame_shape; reasons = set(); face_lm = face_landmarks.landmark
        L_EYE=[362,385,387,263,373,380]; R_EYE=[33,160,158,133,153,144]
        l_eye_pts = np.array([(face_lm[i].x * w, face_lm[i].y * h) for i in L_EYE])
        r_eye_pts = np.array([(face_lm[i].x * w, face_lm[i].y * h) for i in R_EYE])
        ear = (self._calculate_ear(l_eye_pts) + self._calculate_ear(r_eye_pts)) / 2.0
        if ear < self.EAR_THRESHOLD: self.drowsy_counter = min(self.drowsy_counter + 1, 30)
        else: self.drowsy_counter = max(self.drowsy_counter - 1, 0)
        if self.drowsy_counter > 20: reasons.add("Drowsy")
        MOUTH=[61, 291, 0, 17]; mouth_pts = np.array([(face_lm[i].x * w, face_lm[i].y * h) for i in MOUTH])
        mouth_h_dist = np.linalg.norm(mouth_pts[0] - mouth_pts[1])
        mar = np.linalg.norm(mouth_pts[2] - mouth_pts[3]) / mouth_h_dist if mouth_h_dist > 0 else 0
        if mar > self.YAWN_THRESHOLD: self.yawn_counter = min(self.yawn_counter + 1, 20)
        else: self.yawn_counter = max(self.yawn_counter - 1, 0)
        if self.yawn_counter > 15: reasons.add("Yawning")
        L_IRIS = [474, 475, 476, 477]; R_IRIS = [469, 470, 471, 472]
        l_iris_center = np.mean([(face_lm[i].x * w, face_lm[i].y * h) for i in L_IRIS], axis=0)
        r_iris_center = np.mean([(face_lm[i].x * w, face_lm[i].y * h) for i in R_IRIS], axis=0)
        avg_gaze_ratio = (self._calculate_gaze_ratio(l_eye_pts, l_iris_center) + self._calculate_gaze_ratio(r_eye_pts, r_iris_center)) / 2.0
        if abs(avg_gaze_ratio) > self.GAZE_THRESHOLD: self.gaze_counter = min(self.gaze_counter + 1, 30)
        else: self.gaze_counter = max(self.gaze_counter - 1, 0)
        if self.gaze_counter > 10: reasons.add("Looking Away")
        current_raw_score = 100
        if "Looking Away" in reasons: current_raw_score -= 60
        if "Drowsy" in reasons: current_raw_score -= 40
        if "Yawning" in reasons: current_raw_score -= 30
        self.update_score(current_raw_score)
        status = "Attentive"
        if self.smoothed_score < 50: status = "Inattentive"
        elif self.smoothed_score < 75: status = "Distracted"
        self.attention_log.append({'timestamp': time.time() - self.start_time, 'score': self.smoothed_score, 'status': status, 'reason': ", ".join(sorted(reasons))})
        return status, int(self.smoothed_score)
    def generate_report(self):
        # This function and the _generate pages are complex but correct. No changes needed.
        if len(self.attention_log) < self.MIN_FRAMES_FOR_REPORT:
            print(f"Session for {self.name} was too short. Report skipped."); return None
        df = pd.DataFrame(self.attention_log)
        filename = f"report_{self.name.replace(' ', '_')}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        filepath = os.path.join(self.report_dir, filename)
        sns.set_theme(style="whitegrid", palette="colorblind"); print(f"Generating report for {self.name}...")
        try:
            with PdfPages(filepath) as pdf: self._generate_summary_page(pdf, df); self._generate_timeline_page(pdf, df); self._generate_distraction_analysis_page(pdf, df)
            print(f"Report generated: {filepath}"); return filename
        except Exception as e: print(f"CRITICAL ERROR generating report for {self.name}: {e}"); return None
    def _generate_summary_page(self, pdf, df):
        fig = plt.figure(figsize=(8.5, 11)); avg_score = df['score'].mean()
        status = "Excellent" if avg_score >= 80 else "Good" if avg_score >= 60 else "Needs Improvement"
        color = {"Excellent": "#28a745", "Good": "#ffc107", "Needs Improvement": "#dc3545"}[status]
        fig.text(0.5, 0.92, "Attentiveness & Engagement Report", ha='center', fontsize=22, weight='bold')
        fig.text(0.5, 0.87, f"Participant: {self.name}", ha='center', fontsize=18)
        fig.text(0.5, 0.8, f"Overall Engagement: {avg_score:.1f}% ({status})", ha='center', fontsize=16, color=color, weight='bold')
        df['duration'] = df['timestamp'].diff().fillna(0); summary_text = f"This report summarizes an observed session lasting {df['timestamp'].max()/60:.1f} minutes."
        fig.text(0.1, 0.7, summary_text, ha='left', va='top', fontsize=11)
        ax = fig.add_axes([0.1, 0.2, 0.8, 0.4]); status_counts = df['status'].value_counts()
        status_colors = {'Attentive': '#28a745', 'Distracted': '#ffc107', 'Inattentive': '#dc3545'}
        pie_colors = [status_colors.get(s, '#6c757d') for s in status_counts.index]
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=pie_colors,
               wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}, startangle=90, textprops={'fontsize': 14, 'weight': 'bold'})
        ax.set_title('Time Spent in Each Engagement State', fontsize=16); plt.axis('off'); pdf.savefig(fig, bbox_inches='tight'); plt.close()
    def _generate_timeline_page(self, pdf, df):
        fig, ax = plt.subplots(figsize=(11, 8.5)); time_ax = df['timestamp'] / 60
        ax.plot(time_ax, df['score'], color='royalblue', label='Engagement Score', zorder=2, linewidth=2.5)
        ax.fill_between(time_ax, 0, df['score'], color='royalblue', alpha=0.1)
        ax.axhline(y=75, color='orange', linestyle='--', linewidth=1.5, label='Distracted Threshold')
        ax.axhline(y=50, color='red', linestyle='--', linewidth=1.5, label='Inattentive Threshold')
        ax.set_title('Smoothed Engagement Timeline', fontsize=18, weight='bold'); ax.set_xlabel('Time (minutes)', fontsize=14); ax.set_ylabel('Engagement Score (0-100)', fontsize=14)
        ax.legend(loc='lower left', frameon=True, shadow=True, fontsize=12)
        ax.set_ylim(0, 105); ax.set_xlim(0, max(1, time_ax.max())); fig.tight_layout(); pdf.savefig(fig); plt.close()
    def _generate_distraction_analysis_page(self, pdf, df):
        fig = plt.figure(figsize=(8.5, 11)); dist_df = df[df['reason'].str.len() > 0]['reason'].str.split(', ').explode().value_counts()
        if not dist_df.empty:
            ax = fig.add_axes([0.1, 0.1, 0.8, 0.8]); sns.barplot(x=dist_df.values, y=dist_df.index, ax=ax, palette='viridis', orient='h')
            ax.set_title('Frequency of Distraction Triggers', fontsize=16, weight='bold'); ax.set_xlabel('Number of Detections', fontsize=12)
        else: fig.text(0.5, 0.5, 'No Specific Distractions Recorded', ha='center', va='center', fontsize=14)
        pdf.savefig(fig, bbox_inches='tight'); plt.close()

class ClassroomMonitor:
    def __init__(self):
        self.students = {}
        self.lock = Lock() # NEW: Create a lock
        self.initialize_models()

    def initialize_models(self):
        print("Initializing AI models..."); self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        print("Models initialized successfully.")

    def reset(self):
        print("Resetting classroom monitor state."); self.students = {}

    def analyze_student_frame(self, student_id, frame):
        # NEW: Use the lock to ensure thread safety and prevent crashes
        with self.lock:
            if student_id not in self.students:
                print(f"New participant detected with ID: {student_id}. Creating new tracker.")
                self.students[student_id] = StudentTracker(student_id)
            
            tracker = self.students[student_id]
            h, w, _ = frame.shape
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)
            
            if results.multi_face_landmarks:
                status, score = tracker.analyze_face(results.multi_face_landmarks[0], (h, w))
                return {"name": tracker.name, "status": status, "score": score}
            else:
                tracker.update_score(tracker.raw_score - 0.5)
                return {"name": tracker.name, "status": "Searching...", "score": int(tracker.smoothed_score)}

    def generate_all_reports(self):
        print("\n--- SESSION COMPLETE: GENERATING ALL REPORTS ---"); report_files = []
        if not self.students:
            print("No participants were tracked."); return []
        print(f"Checking {len(self.students)} tracked participants for report eligibility...")
        for student in self.students.values():
            report_filename = student.generate_report()
            if report_filename: report_files.append({"student_name": student.name, "filename": report_filename})
        if not report_files: print("No participants met the minimum tracking time for a report.")
        return report_files