# 🧠 AI-Powered Attentiveness Monitor for Google Meet

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)

## 🏆 Project Overview

This is a high-performance, hackathon-grade system designed to provide real-time engagement analysis for teachers, presenters, and team leads during Google Meet sessions. It uses a powerful Python backend with a MediaPipe AI model to analyze video streams and a robust Chrome Extension to display the live results directly within the Google Meet interface.

The system tracks every visible participant, including the host, and provides a live, color-coded overlay with a constantly updating engagement score. At the end of the session, it can generate a detailed, multi-page PDF report summarizing the engagement levels of all participants.

---

## 📂 Project Structure

The project is organized into two main components: the backend server and the frontend browser extension. This structure separates the AI logic from the user interface for better maintainability.

```
AI-Attentiveness-Monitor/
├── .gitignore                    # Tells Git which files and folders to ignore (like venv)
├── README.md                     # You are reading it!
│
├── flask_backend/                # Contains all the Python server code
│   ├── attentiveness_monitor.py  # The core AI analysis logic and report generation
│   ├── app.py                    # The Flask web server that runs the AI
│   └── requirements.txt          # List of Python packages required for the backend
│
└── google_meet_extension/        # Contains all the self-contained Chrome Extension code
    ├── manifest.json             # The extension's blueprint and configuration
    ├── popup.html                # The UI for the extension's popup window
    ├── style.css                 # The stylesheet for the popup
    ├── popup.js                  # The JavaScript logic for the popup buttons
    ├── content.js                # Script injected into Google Meet to draw live overlays
    └── icons/                    # Icons for the browser extension
        ├── icon48.png
        └── icon128.png
```
## ✨ Key Features

*   **🚀 Real-Time Multi-Participant Analysis:** Tracks every visible person simultaneously, providing independent and accurate engagement scores for each.
*   **🧠 Advanced AI Metrics:** Goes beyond simple presence detection by analyzing:
    *   **Gaze Detection:** Detects if a participant is looking away from the screen (e.g., at a phone).
    *   **Drowsiness:** Uses Eye Aspect Ratio (EAR) to detect signs of sleepiness.
    *   **Yawning:** Detects yawning as a potential indicator of fatigue or disinterest.
*   **📊 Live Visual Feedback:** Displays a clean, intuitive overlay on each participant's video tile, including:
    *   A colored border (Green/Yellow/Red) representing their current engagement status.
    *   A text label with their name, live score, and status (e.g., "Attentive", "Distracted").
*   **📋 Comprehensive PDF Reporting:** On-demand generation of a detailed PDF report for every tracked participant, featuring summary charts and engagement timelines. A minimum of 30 seconds of tracking is required to generate a report.
*   **⚡ Optimized Performance:** Built with a state-managed, thread-safe Python backend and a lightweight Chrome Extension to ensure a smooth, lag-free experience.

---

## 🛠️ Tech Stack

*   **Backend:** Python, Flask, OpenCV, MediaPipe
*   **Frontend:** Chrome Extension (JavaScript, HTML, CSS)
*   **Data & Reporting:** Pandas, Matplotlib, Seaborn

---

## ⚙️ Installation & Setup

This project requires setting up both the backend server and the frontend extension.

### 1. Backend Setup

The backend performs all the heavy AI analysis.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```

2.  **Navigate to the Backend Directory**
    ```bash
    cd flask_backend
    ```

3.  **(Recommended) Create and Activate a Python Virtual Environment**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate it (on Windows)
    venv\Scripts\activate

    # Activate it (on macOS/Linux)
    source venv/bin/activate
    ```

4.  **Install Required Packages**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Flask Server**
    ```bash
    python app.py
    ```
    Leave this terminal running. The server is now active and waiting for requests from the extension.

### 2. Frontend Setup

The frontend is the Chrome Extension that you see and interact with.

1.  Open Google Chrome and navigate to `chrome://extensions`.
2.  In the top-right corner, toggle on **"Developer mode"**.
3.  Click the **"Load unpacked"** button that appears on the top-left.
4.  In the file selection dialog, navigate to and select the **`google_meet_extension`** folder from this project.
5.  The "Definitive Attentiveness Monitor" extension will now appear in your list of extensions. Make sure the toggle switch on its card is enabled.

---

## 🚀 How to Use

1.  **Start the Backend Server:** Make sure the `python app.py` command is running in your terminal.
2.  **Join a Google Meet Call:** Start or join any meeting. The extension icon in your toolbar will become active.
3.  **Start Analysis:** Click the extension icon to open the popup, then click the **"Start Analysis"** button.
4.  **View Live Results:** You will immediately see colored borders and score labels appear on all visible participant video tiles. These will update in real-time.
5.  **Generate Reports:** When your session is over, click the extension icon again and click **"End & Get Reports"**.
    *   For a report to be generated, a participant must be tracked for a **minimum of 30 seconds**.
    *   Download links for the generated PDF reports will appear in the popup.

---

## ⚠️ Important Note

This extension relies on identifying video elements on the Google Meet webpage using their HTML structure. Google may update its website layout at any time, which could temporarily break the extension's ability to find videos. If this happens, the CSS selectors in the `content.js` file may need to be updated.
