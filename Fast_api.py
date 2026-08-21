from fastapi import(
     FastAPI,
     UploadFile,
     File,
     HTTPException,
     Request
)
from fastapi.responses import FileResponse

import cv2
import os
import sys
import numpy as np
import uuid

# Add src directory to system path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


# ============================================================
# IMPORT OUR PROJECT MODULES
# ============================================================

from src.Detection import (
    run_detection,
    run_image_detection
)
from src.Tracking import track_detections
from src.Analysis import (
    analyze_defects,
    analyze_image_defects
)
from src.Report import (
    generate_report,
    generate_image_report
)

from opencv.preprocessing import preprocess_images
from opencv.alignment import align_images, apply_transform_color
from opencv.detection import detect_missing_print, draw_defect_boxes
from opencv.defect_analysis import DefectAnalyzer
from opencv.qc_reprt import QCReportGenerator


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(

    title=
        "Textile Fabric Defect Detection API",

    description=
        "YOLOv8 based textile defect detection and QC system",

    version="1.0.0"
)


# ============================================================
# DIRECTORIES
# ============================================================

UPLOAD_DIR = "uploaded_videos"

IMAGE_DIR = "uploaded_images"

REPORT_DIR = "reports"


os.makedirs(

    UPLOAD_DIR,

    exist_ok=True

)

os.makedirs(

    IMAGE_DIR,

    exist_ok=True
)


os.makedirs(

    REPORT_DIR,

    exist_ok=True

)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {

        "success": True,

        "message":
            "Textile Fabric Defect Detection API is running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "running",

        "modules": {

            "detection":
                "connected",

            "tracking":
                "connected",

            "analysis":
                "connected",

            "report":
                "connected"
        }
    }


# ============================================================
# SAVE VIDEO
# ============================================================

async def save_video( video: UploadFile):

    allowed_extensions = (

        ".mp4",

        ".avi",

        ".mov",

        ".mkv",

        ".webm"

    )


    if not video.filename:

        raise HTTPException(

            status_code=400,

            detail=
                "No filename provided."
        )


    extension = os.path.splitext(video.filename)[1].lower()


    if extension not in allowed_extensions:

        raise HTTPException(

            status_code=400,

            detail=
                "Unsupported video format."
        )


    unique_filename = (

        f"{uuid.uuid4().hex}"

        f"{extension}"

    )


    video_path = os.path.join(

        UPLOAD_DIR,

        unique_filename
    )


    with open(

        video_path,

        "wb"

    ) as file:

        while True:

            chunk = await video.read(

                1024 * 1024

            )


            if not chunk:

                break


            file.write(
                chunk
            )


    return video_path


# ============================================================
# SAVE IMAGE
# ============================================================

async def save_image(
    image: UploadFile
):

    allowed_extensions = (
        ".jpg",
        ".jpeg",
        ".png"
    )

    # --------------------------------------------------------
    # Check filename
    # --------------------------------------------------------

    if not image.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    # --------------------------------------------------------
    # Get extension
    # --------------------------------------------------------

    extension = os.path.splitext(
        image.filename
    )[1].lower()

    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Unsupported image format."
        )

    # --------------------------------------------------------
    # Create unique filename
    # --------------------------------------------------------

    unique_filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    image_path = os.path.join(
        IMAGE_DIR,
        unique_filename
    )

    # --------------------------------------------------------
    # Save image
    # --------------------------------------------------------

    with open(
        image_path,
        "wb"
    ) as file:

        while True:

            chunk = await image.read(
                1024 * 1024
            )

            if not chunk:
                break

            file.write(chunk)

    return image_path


# ============================================================
# MAIN PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
async def predict_video(
    request: Request,
    video: UploadFile = File(...)
):

    report_id = uuid.uuid4().hex


    try:

        # ----------------------------------------------------
        # 1. SAVE VIDEO
        # ----------------------------------------------------

        video_path = await save_video(video)


        # ----------------------------------------------------
        # 2. YOLO + BYTE TRACK
        # ----------------------------------------------------

        detection_result = run_detection(video_path)

        # ====================================================
        # GET REPRESENTATIVE DEFECT FRAMES
        # ====================================================

        representative_frames = (
            detection_result.get(
                "representative_frames",
                []
                )
            )


        # ----------------------------------------------------
        # 3. BUILD TRACKED DEFECT RECORDS
        # ----------------------------------------------------

        tracking_result = track_detections(detection_result)


        # ----------------------------------------------------
        # 4. DEFECT ANALYSIS
        # ----------------------------------------------------

        qc_data = analyze_defects(tracking_result)


        # ----------------------------------------------------
        # 5. REPORT
        # ----------------------------------------------------

        report_data = generate_report(

            qc_data,

            report_id,

            video.filename,

            REPORT_DIR,

            representative_frames

        )
        # ====================================================
        # 5. CREATE PDF URL
        # ====================================================

        base_url = str(
            request.base_url
        ).rstrip("/")


        pdf_url = (
            f"{base_url}"
            f"/report/{report_id}/pdf"
        )

        # ----------------------------------------------------
        # 6. RESPONSE
        # ----------------------------------------------------

        return {

            "success": True,

            "message":
                "Video processed successfully",

            "report_id":
                report_id,

            "video":
                qc_data["video_info"],

            "summary":
                qc_data["summary"],

            "defects":
                qc_data["defects"],

            "reports":
                report_data
   
        }


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)

        )

# ============================================================
# IMAGE PREDICTION ENDPOINT
# ============================================================

@app.post("/predict/image")
async def predict_image(
    request: Request,
    image: UploadFile = File(...)
):

    report_id = uuid.uuid4().hex

    try:

        # ====================================================
        # 1. SAVE IMAGE
        # ====================================================

        image_path = await save_image(
            image
        )


        # ====================================================
        # 2. IMAGE DETECTION
        # ====================================================

        detection_result = run_image_detection(
            image_path
        )

        # ====================================================
        # 3. SAVE ANNOTATED IMAGE
        # ====================================================

        annotated_image = detection_result["annotated_image"]

        annotated_image_path = os.path.join(

            REPORT_DIR,
            f"{report_id}_annotated.jpg"
        )

        cv2.imwrite(
            annotated_image_path,
            annotated_image
        )


        # ====================================================
        # 3. DEFECT ANALYSIS
        # ====================================================

        qc_data = analyze_image_defects(
            detection_result
        )


        # ====================================================
        # 4. GENERATE REPORT
        # ====================================================

        report_data = generate_image_report(

            qc_data,

            report_id,

            image.filename,

            REPORT_DIR,

            annotated_image_path

        )


        # ====================================================
        # 5. CREATE PDF URL
        # ====================================================

        base_url = str(
            request.base_url
        ).rstrip("/")


        pdf_url = (
            f"{base_url}"
            f"/report/{report_id}/pdf"
        )


        # ====================================================
        # 6. RESPONSE
        # ====================================================

        return {

            "success": True,

            "message":
                "Image processed successfully",

            "report_id":
                report_id,

            "defects":
                qc_data["defects"],

            "summary":
                qc_data["summary"],

            "pdf":
                pdf_url,

            "annotated_image":
                f"/report/{report_id}/image"    
        }


    except Exception as error:


        import traceback

        traceback.print_exc()

        raise HTTPException(

            status_code=500,

            detail=str(error)

        )


# ============================================================
# GET JSON REPORT
# ==============================================================

@app.get("/report/{report_id}/json")
def get_report(report_id: str):
      

    report_path = os.path.join(

        REPORT_DIR,

        f"{report_id}.json"

    )


    if not os.path.exists(
        report_path
    ):

        raise HTTPException(

            status_code=404,

            detail="Report not found."
        )


    return FileResponse(

        report_path,

        media_type="application/json",

        filename=
            f"QC_Report_{report_id}.json"
    )


# ============================================================
# GET HTML REPORT
# ============================================================

@app.get("/report/{report_id}/html")
def get_html_report(report_id: str ):


    report_path = os.path.join(

        REPORT_DIR,

        f"{report_id}.html"

    )


    if not os.path.exists(
        report_path
    ):

        raise HTTPException(

            status_code=404,

            detail="HTML report not found."
        )


    return FileResponse(

        report_path,

        media_type="text/html",

        filename=
            f"QC_Report_{report_id}.html"
    )


# ============================================================
# DOWNLOAD PDF REPORT
# ============================================================


@app.get("/report/{report_id}/pdf")
def get_pdf_report(report_id: str ):

    report_path = os.path.join(

        REPORT_DIR,

        f"{report_id}.pdf"

    )


    if not os.path.exists(
        report_path
    ):

        raise HTTPException(

            status_code=404,

            detail="PDF report not found."
        )


    return FileResponse(

        report_path,

        media_type="application/pdf",

        filename=
            f"QC_Report_{report_id}.pdf"
    )


#============================================================
# GET ANNOTATED IMAGE
#============================================================

@app.get("/report/{report_id}/image")
async def get_report_image(report_id: str):

    image_path = os.path.join(
        REPORT_DIR,
        f"{report_id}_annotated.jpg"
    )

    if not os.path.exists(image_path):

        raise HTTPException(
            status_code=404,
            detail="Annotated image not found"
        )

    return FileResponse(
        image_path,
        media_type="image/jpeg"
    )

#===================================================
# READ IMAGE FROM UPLOAD
#===================================================


async def read_image_from_upload(upload_file: UploadFile):
    """Decode uploaded file directly into an OpenCV BGR image."""
    contents = await upload_file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(
            status_code=400,
            detail=f"Could not decode image: {upload_file.filename}"
        )
    return image


# ============================================================
# OPENCV PRINT INSPECTION ENDPOINT
# ============================================================

@app.post("/predict/print-inspection")
async def predict_print_inspection(
    request: Request,
    reference_image: UploadFile = File(...),
    factory_image: UploadFile = File(...)
):
    report_id = uuid.uuid4().hex

    try:
        # 1. Load and decode uploaded images
        ref_img = await read_image_from_upload(reference_image)
        fac_img = await read_image_from_upload(factory_image)

        # 2. Preprocess and Align
        ref_gray, fac_gray, fac_resized_color = preprocess_images(ref_img, fac_img)
        fac_aligned, valid_mask, transform_info = align_images(ref_gray, fac_gray)

        height, width = ref_gray.shape[:2]
        fac_aligned_color = apply_transform_color(
            fac_resized_color, transform_info, (width, height)
        )

        # 3. Detect Missing Print Defects
        missing_mask, missing_defects, _, _ = detect_missing_print(
            ref_img, fac_aligned_color, valid_mask=valid_mask, saturation_threshold=50, min_area=100
        )

        # 4. Draw Annotations & Save Image
        annotated_image = draw_defect_boxes(fac_aligned_color, missing_defects)
        annotated_image_path = os.path.join(REPORT_DIR, f"{report_id}_annotated.jpg")
        cv2.imwrite(annotated_image_path, annotated_image)

        # 5. Format payload & run DefectAnalyzer
        formatted_defects = []
        for d in missing_defects:
            ymin = int((d["y"] / height) * 1000)
            xmin = int((d["x"] / width) * 1000)
            ymax = int(((d["y"] + d["height"]) / height) * 1000)
            xmax = int(((d["x"] + d["width"]) / width) * 1000)

            formatted_defects.append({
                "defect_type": "missing_print",
                "box_2d": [ymin, xmin, ymax, xmax],
                "confidence": 0.95,
                "description": f"Missing print defect detected (area: {d.get('area', 0)}px)."
            })

        analyzer = DefectAnalyzer()
        analysis_result = analyzer.analyze({
            "defect_detected": len(formatted_defects) > 0,
            "defects": formatted_defects
        })
        json_path = os.path.join(REPORT_DIR, f"{report_id}.json")
        analyzer.save_result(analysis_result, json_path)

        # 6. Generate PDF QC Report
        generator = QCReportGenerator(output_directory=REPORT_DIR)
        generated_pdf = generator.generate(analysis_result, annotated_image=annotated_image_path)
        
        target_pdf_path = os.path.join(REPORT_DIR, f"{report_id}.pdf")
        if os.path.exists(generated_pdf) and generated_pdf != target_pdf_path:
            os.replace(generated_pdf, target_pdf_path)

        base_url = str(request.base_url).rstrip("/")

        return {
            "success": True,
            "inspection_type": "opencv_print_comparison",
            "report_id": report_id,
            "status": analysis_result["inspection_status"],
            "total_defects": analysis_result["total_defects"],
            "defects": analysis_result["defects"],
            "pdf_url": f"{base_url}/report/{report_id}/pdf",
            "json_url": f"{base_url}/report/{report_id}/json",
            "annotated_image_url": f"{base_url}/report/{report_id}/image"
        }

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(error))