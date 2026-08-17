# Textile Fabric Defect Detection & QC System

Automated textile quality control system using **YOLOv8** deep learning for defect detection, **ByteTrack** for multi-object tracking, and automatic **PDF QC report** generation.

## Features

- **Image Analysis** — Upload a fabric image, detect defects with bounding boxes, get instant QC results
- **Video Analysis** — Upload inspection video, track defects across frames, generate full QC report
- **Live Camera** — Capture fabric images from webcam for real-time defect detection
- **Automatic QC Reports** — PDF reports generated automatically with defect details, locations, and confidence scores
- **Annotated Output** — Images returned with bounding boxes drawn around detected defects

## Architecture

```
Streamlit Frontend (app.py)
        |
        | HTTP Requests
        |
FastAPI Backend (Fast_api.py)
        |
   YOLOv8 + ByteTrack (Detection.py)
        |
   Defect Tracking (Tracking.py)
        |
   Defect Analysis (Analysis.py)
        |
   PDF Report Generation (Report.py)
        |
   Results → Frontend
```

## Project Structure

```
final_project/
├── app.py                 # Streamlit frontend dashboard
├── api_client.py          # HTTP client for FastAPI communication
├── ui_components.py       # UI styling and component helpers
├── Fast_api.py            # FastAPI backend server
├── Detection.py           # YOLOv8 detection + ByteTrack tracking
├── Tracking.py            # Defect tracking logic
├── Analysis.py            # Defect analysis and statistics
├── Report.py              # PDF/HTML/JSON report generation
├── best.pt                # YOLOv8 trained model weights
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
├── uploaded_images/       # Runtime: uploaded images
├── uploaded_videos/       # Runtime: uploaded videos
└── reports/               # Runtime: generated QC reports
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/final_project.git
cd final_project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download model weights

Place the YOLOv8 trained model file `best.pt` in the project root directory.

> **Note:** The `best.pt` file is not included in the repository due to its size (~22 MB). You need to obtain it separately.

### 4. Start the FastAPI backend

```bash
uvicorn Fast_api:app --reload --port 8000
```

### 5. Start the Streamlit frontend (in a new terminal)

```bash
streamlit run app.py --server.port 8501
```

### 6. Open in browser

Go to: **http://localhost:8501**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API health message |
| `GET` | `/health` | Module connection status |
| `POST` | `/predict/image` | Upload image for defect detection |
| `POST` | `/predict` | Upload video for full QC analysis |
| `GET` | `/report/{report_id}/pdf` | Download PDF QC report |
| `GET` | `/report/{report_id}/image` | Get annotated image with bounding boxes |
| `GET` | `/report/{report_id}/json` | Get JSON report data |
| `GET` | `/report/{report_id}/html` | Get HTML report |

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI + Uvicorn
- **Detection:** YOLOv8 (Ultralytics)
- **Tracking:** ByteTrack
- **Computer Vision:** OpenCV
- **Reports:** ReportLab (PDF)
- **HTTP Client:** Requests
