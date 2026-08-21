<div align="center">

# 🏭 Textile Fabric Defect Detection & QC System

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**An end-to-end industrial quality control system combining YOLOv8 Deep Learning detection, ByteTrack multi-object tracking, OpenCV image registration & print comparison, and automated PDF Quality Control (QC) reporting.**

</div>

---

## 📖 1. About & Project Overview

Textile manufacturing and garment printing industries face critical quality assurance challenges. Flaws such as holes, cuts, color staining, gray stitches, contamination, or missing print patterns can compromise entire production batches if undetected.

**Textile Fabric Defect Detection & QC System** is an end-to-end inspection platform designed to automate and standardize this process with two specialized inspection engines:

1. **Deep Learning Engine (YOLOv8 + ByteTrack):** Detects surface-level fabric anomalies (stains, cuts, holes, contaminations) across static images, moving video rolls, and live webcam streams with persistent object tracking.
2. **Computer Vision Engine (OpenCV Image Registration & Difference Analysis):** Compares a factory manufactured print against a reference ground-truth design, performs sub-pixel alignment, and highlights missing, blurred, or defective print regions.

Both engines feed into an automated **ReportLab PDF generation engine**, producing formal inspection documentation with defect tables, bounding boxes, and compliance statuses.

---

## ✨ 2. Key Features

| Feature | Description |
| :--- | :--- |
| **📷 Image Defect Detection** | Upload single fabric images (JPG, JPEG, PNG) for instant YOLOv8 inference and spatial defect localization. |
| **🎬 Video Inspection & Tracking** | Track defects across moving fabric conveyor lines with ByteTrack to calculate unique defect counts without duplicates. |
| **📹 Live Camera & Video Recorder** | Capture live frames or record conveyor video directly in the browser for immediate quality assessment. |
| **🖨️ OpenCV Print Inspection** | Compare a Reference print against a Factory print with automatic ORB/ECC alignment to detect missing print defects. |
| **🖼️ Annotated Defect Visuals** | Generates high-resolution annotated images with labeled bounding boxes and defect metrics. |
| **📄 Automated PDF QC Reports** | Generates downloadable, formal industrial PDF reports containing defect breakdowns, metrics, and timestamps. |
| **📊 Defect Analytics & Metrics** | Live metrics for total defects, defect class breakdown, unique counts, most frequent flaw, and PASS/FAIL rating. |
| **🔌 Decoupled REST API** | FastAPI backend exposing REST endpoints for prediction, image retrieval, and PDF document generation. |

---

## 🛠️ 3. Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python** | Core programming language |
| **FastAPI / Uvicorn** | High-performance asynchronous REST API backend |
| **Streamlit** | Industrial quality control dashboard frontend |
| **YOLOv8 (Ultralytics)** | Deep learning object detection for fabric surface flaws |
| **ByteTrack** | Persistent multi-object tracking across video frames |
| **OpenCV (`cv2`)** | Feature alignment (ORB), perspective warping, color difference masking, and contour detection |
| **ReportLab** | Formal PDF Quality Control report compilation |
| **NumPy & Pandas** | Image matrix processing, defect tabular structures, and analytics |
| **Pillow (PIL)** | Image manipulation and format conversions |
| **Requests** | HTTP client for Streamlit-to-FastAPI communication |

---

## 🧠 4. Inspection Engines & Detection Pipelines

```
                                  INSPECTION MODES
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
[ Deep Learning Pipeline ]                                   [ OpenCV Print Inspection Pipeline ]
  • YOLOv8 Detection                                           • Image Preprocessing & Grayscale
  • ByteTrack Multi-Object Tracking                            • Feature Extraction & Alignment (ORB/ECC)
  • Spatial Defect Localization                                • Color / Saturation Difference Masking
  • Classes: Stain, Cut, Hole, etc.                            • Missing Print Contour Extraction
        │                                                                 │
        └────────────────────────────────┬────────────────────────────────┘
                                         ▼
                             [ Defect Analytics Engine ]
                                         ▼
                            [ PDF QC Report Generator ]
```

### 1. Deep Learning Surface Detection (`src/`)
* **YOLOv8 Inference:** Identifies fabric flaws, producing normalized bounding boxes `[x1, y1, x2, y2]`.
* **ByteTrack Association:** Assigns persistent Track IDs (`D001`, `D002`...) across consecutive video frames to prevent over-counting.
* **Spatial Categorization:** Maps defect placement (e.g., *Top-Left*, *Center-Middle*, *Bottom-Right*).

### 2. OpenCV Print Comparison (`opencv/`)
* **Preprocessing & Alignment (`alignment.py`):** Uses ORB feature matching and Homography transformations to align the factory image with the reference design regardless of camera tilt or scale.
* **Missing Print Detection (`detection.py`):** Calculates saturation and color difference masks to extract missing pattern contours.
* **Defect Analyzer (`defect_analysis.py`):** Quantifies defective area sizes in pixels, determines pass/fail thresholds, and normalizes coordinates.
* **Print QC Reporter (`qc_reprt.py`):** Compiles specialized side-by-side comparison metrics into printable PDF records.

---

## 🗂️ 5. Project Structure

```directory
final_project/
├── .gitignore                      # Git ignore file for cache, temporary uploads, and generated reports
├── Fast_api.py                     # FastAPI server hosting YOLOv8 and OpenCV prediction endpoints
├── app.py                          # Streamlit UI dashboard with 4 inspection modes
├── best.pt                         # Fine-tuned YOLOv8 model weights (~22 MB)
├── README.md                       # Comprehensive system documentation and architecture guide
├── requirements.txt                # Python package dependencies
│
├── src/                            # YOLOv8 Deep Learning & Core Frontend Modules
│   ├── __init__.py
│   ├── Analysis.py                 # Defect metrics aggregation and statistical summaries
│   ├── Detection.py                # YOLOv8 inference on single images and video streams
│   ├── Report.py                   # ReportLab PDF & HTML generation engine for YOLO detections
│   ├── Tracking.py                 # ByteTrack tracking integration and track record builder
│   ├── api_client.py               # Streamlit HTTP client interface connecting to FastAPI
│   ├── ui_components.py            # Custom UI cards, responsive tables, and adaptive CSS theme
│   └── camera_component/           # Custom HTML5/JS webcam component for in-browser recording
│       └── index.html
│
├── opencv/                         # Traditional Computer Vision & Print Inspection Modules
│   ├── __init__.py
│   ├── alignment.py                # ORB feature detection, homography matrix & perspective warping
│   ├── preprocessing.py            # Image grayscale conversion, sizing, and normalization
│   ├── detection.py                # Missing print defect segmentation and bounding box drawer
│   ├── defect_analysis.py          # Defect severity calculation and status determination (PASS/FAIL)
│   ├── qc_reprt.py                 # Dedicated PDF report generator for print comparison
│   ├── input.py                    # Input image validation and file reading utilities
│   ├── main.py                     # Standalone CLI entrypoint for local OpenCV testing
│   └── sample_images/              # Reference and factory defect print test samples
│
├── notebooks/                      # Data Science & Machine Learning Research
│   ├── 01_EDA.ipynb                # Exploratory Data Analysis on textile defect dataset
│   ├── 02_Model_Training.ipynb     # YOLOv8 fine-tuning and training routines
│   └── 03_Model_Evaluation.ipynb   # Precision, Recall, and mAP performance evaluation
│
├── uploaded_images/                # [Runtime] Storage for incoming uploaded image files
├── uploaded_videos/                # [Runtime] Storage for incoming video files
└── reports/                        # [Runtime] Storage for generated annotated images, JSON, and PDF reports
```

---

## 🚀 6. Quick Start Guide

### Prerequisites
* Python `3.10`, `3.11`, or `3.12` installed.
* Git installed.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-Musa-kazmi/Textile-Fabric-Defect-Detection-QC-System.git
   cd Textile-Fabric-Defect-Detection-QC-System
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ 7. Running the Application

The system requires running both the **FastAPI Backend** and the **Streamlit Frontend**:

### Step 1: Launch FastAPI Backend
```bash
python -m uvicorn Fast_api:app --port 8000 --host 127.0.0.1
```
* API Server: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
* Interactive API Documentation (Swagger UI): **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Step 2: Launch Streamlit Dashboard
```bash
streamlit run app.py --server.port 8501
```
* Dashboard URL: **[http://localhost:8501](http://localhost:8501)**

---

## ☁️ 8. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status and root greeting |
| `GET` | `/health` | Health check verifying status of all connected modules |
| `POST` | `/predict/image` | Analyzes a single image for defects using YOLOv8 |
| `POST` | `/predict` | Processes video rolls with YOLOv8 detection + ByteTrack tracking |
| `POST` | `/predict/print-inspection` | Compares Reference vs. Factory prints using OpenCV image registration |
| `GET` | `/report/{report_id}/image` | Fetches the annotated image with rendered defect bounding boxes |
| `GET` | `/report/{report_id}/pdf` | Downloads the generated Quality Control PDF report |
| `GET` | `/report/{report_id}/json` | Fetches raw defect JSON records and metadata |
| `GET` | `/report/{report_id}/html` | Fetches the HTML-rendered QC report |

---

## 👤 9. Author

- **Musa Kazmi**
- **GitHub**: [@Musa-kazmi](https://github.com/Musa-kazmi)
- **LinkedIn**: [Musa Kazmi](https://www.linkedin.com/in/musa-kazmi-6b99973b4)
- **Email**: kazmi6261@gmail.com

---

## 📄 10. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
