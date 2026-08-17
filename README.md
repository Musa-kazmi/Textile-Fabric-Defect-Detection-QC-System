<div align="center">

# 🏭 Textile Fabric Defect Detection & QC System

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Automated industrial textile fabric defect detection, multi-object tracking, and automated PDF QC report generation powered by YOLOv8, ByteTrack, FastAPI, and Streamlit.**

</div>

---

## 📖 1. About & Project Overview

Textile manufacturing plants face significant quality control challenges when manually inspecting fabrics for flaws like stains, holes, cuts, contamination, color variations, or gray stitches. Manual inspection is slow, prone to human error, and lacks standardized reporting.

**Textile Fabric Defect Detection & QC System** automates this entire pipeline. Using a fine-tuned **YOLOv8** computer vision model combined with **ByteTrack** multi-object tracking, the system detects and tracks fabric flaws in real-time across images, videos, and live webcam feeds. It automatically generates formal, industry-grade **PDF Quality Control (QC) Reports** with complete spatial defect counts, confidence scores, and bounding box annotations accessible via a clean Streamlit dashboard backed by a RESTful FastAPI backend.

---

## ✨ 2. Key Features

| Feature | Description |
| :--- | :--- |
| **📷 Image Defect Detection** | Upload fabric images (JPG, JPEG, PNG) for instant defect detection and spatial bounding box overlays. |
| **🎬 Video Inspection & Tracking** | Process fabric rolls in motion using YOLOv8 + ByteTrack to count unique defects without double-counting. |
| **📹 Live Camera Mode** | Capture live fabric samples from a webcam feed for real-time quality control checks. |
| **🖼️ Annotated Output** | Returns rendered images with bounding boxes drawn directly around detected defects. |
| **📄 Automatic PDF QC Reports** | Generates downloadable, formal PDF quality control reports with defect breakdowns and metrics. |
| **📊 Defect Analytics & Metrics** | Displays total defect counts, unique defect types, most common flaw, and confidence scores. |
| **🔌 Decoupled REST API** | Fully decoupled architecture using FastAPI HTTP REST endpoints to handle model inference. |

---

## 🛠️ 3. Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python** | Primary programming language |
| **FastAPI / Uvicorn** | High-performance asynchronous REST API backend |
| **Streamlit** | Modern industrial frontend dashboard |
| **YOLOv8 (Ultralytics)** | Deep learning object detection model |
| **ByteTrack** | Real-time multi-object defect tracking across video frames |
| **OpenCV** | Image & video processing, frame annotation, and bounding box drawing |
| **ReportLab** | Automated PDF Quality Control report generation |
| **Pandas & NumPy** | Data manipulation and statistical calculations |
| **Requests** | HTTP client for Streamlit to FastAPI communication |

---

## 🧠 4. Model & Detection Pipeline

The core intelligence is powered by **YOLOv8** trained specifically on textile fabric defect datasets to recognize common defect classes such as *Stain*, *Contamination*, *Color Issues*, *Gray Stitch*, *Cut*, and *Hole*.

| Component | Responsibility |
| :--- | :--- |
| **YOLOv8 Engine** | Locates defects in individual frames/images and produces bounding box coordinates `[x1, y1, x2, y2]`. |
| **ByteTrack Tracker** | Assigns persistent Track IDs (`D001`, `D002`, etc.) across moving video frames to prevent duplicate counts. |
| **Defect Analyzer** | Categorizes spatial placement (e.g., *Top-Left*, *Middle-Center*) and calculates confidence metrics. |
| **Report Engine** | Compiles defect counts into formatted JSON, HTML, and printable PDF documents. |

---

## 📈 5. Pipeline Architecture & Workflow

```
                        FRONTEND (Streamlit)
                                 |
            +--------------------+--------------------+
            |                    |                    |
       IMAGE UPLOAD         VIDEO UPLOAD         LIVE CAMERA
            |                    |                    |
            +--------------------+--------------------+
                                 |
                             HTTP POST
                                 |
                        BACKEND (FastAPI)
                                 |
                         YOLOv8 + OpenCV
                                 |
                             ByteTrack
                                 |
                          Defect Analysis
                                 |
                        PDF Report Generation
                                 |
                             HTTP GET
                                 |
                        FRONTEND (Streamlit)
                                 |
               [ View Results & Download PDF QC Report ]
```

---

## 🗂️ 6. Project Structure

```directory
final_project/
├── .gitignore              # Tells Git which files to ignore (cache, uploads, reports, models)
├── Analysis.py             # Defect statistical analysis and summary aggregation
├── Detection.py            # YOLOv8 inference and image/video frame processing
├── Fast_api.py             # FastAPI REST server providing prediction and report endpoints
├── Report.py               # ReportLab PDF and HTML report generation engine
├── Tracking.py             # ByteTrack defect tracking data structure builder
├── api_client.py           # Streamlit HTTP client wrapper for FastAPI communication
├── app.py                  # Streamlit main frontend application
├── best.pt                 # Trained YOLOv8 model weights (~22 MB)
├── README.md               # Project documentation and setup guide
├── requirements.txt        # List of Python dependencies
├── ui_components.py        # Custom industrial UI layout, metrics, and dataframe components
├── reports/                # [Runtime] Storage for generated PDF, JSON, and HTML reports
├── uploaded_images/        # [Runtime] Temporary storage for uploaded image files
└── uploaded_videos/        # [Runtime] Temporary storage for uploaded video files
```

---

## 🚀 7. Quick Start Guide

### Prerequisites
- Python 3.10 - 3.12 installed on your system.
- Git installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Textile-Fabric-Defect-Detection-QC-System.git
   cd Textile-Fabric-Defect-Detection-QC-System
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   # Create environment
   python -m venv venv
   
   # Activate environment (Windows)
   .\venv\Scripts\activate
   
   # Activate environment (Linux/macOS)
   source venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

### How to Run

1. **Start the FastAPI Backend (Terminal 1):**
   ```bash
   uvicorn Fast_api:app --reload --port 8000
   ```
   *Backend runs at: [http://127.0.0.1:8000](http://127.0.0.1:8000)*

2. **Start the Streamlit Frontend (Terminal 2):**
   ```bash
   streamlit run app.py --server.port 8501
   ```
   *Frontend opens at: [http://localhost:8501](http://localhost:8501)*

---

## ☁️ 8. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status check |
| `GET` | `/health` | Verification of all pipeline modules |
| `POST` | `/predict/image` | Analyzes image file and returns defect list, summary, and annotated image URL |
| `POST` | `/predict` | Processes video file using YOLOv8 + ByteTrack and returns full QC statistics |
| `GET` | `/report/{report_id}/pdf` | Downloads the generated PDF Quality Control report |
| `GET` | `/report/{report_id}/image` | Fetches the annotated image with bounding boxes drawn |
| `GET` | `/report/{report_id}/json` | Fetches raw JSON report data |
| `GET` | `/report/{report_id}/html` | Fetches HTML version of the QC report |

---

## 👤 9. Author

- **Musa Kazmi**
- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [@your-profile](https://linkedin.com/in/your-profile)

---

## 📄 10. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
