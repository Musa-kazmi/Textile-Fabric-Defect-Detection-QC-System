"""
API Client for Textile Fabric Defect Detection & QC System
===========================================================
Centralized HTTP communication layer.
All FastAPI requests go through this module.
The Streamlit app never calls requests/fetch directly.
"""

import requests
import io


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# HEALTH CHECK
# ============================================================

def check_health():
    """
    Check if FastAPI backend is running and reachable.
    Returns dict with status info, or None on failure.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.ConnectionError:
        return None

    except requests.exceptions.Timeout:
        return None

    except Exception:
        return None


# ============================================================
# UPLOAD IMAGE FOR PREDICTION
# ============================================================

def upload_image(image_bytes, filename):
    """
    Send an image to FastAPI for defect detection.

    Args:
        image_bytes: Raw bytes of the image file.
        filename: Original filename (e.g., 'fabric_sample.jpg').

    Returns:
        dict: API response with defects, summary, pdf url,
              and annotated_image path.
        None: On failure (with error message printed).
    """
    try:
        files = {
            "image": (
                filename,
                image_bytes,
                _get_image_content_type(filename)
            )
        }

        response = requests.post(
            f"{API_BASE_URL}/predict/image",
            files=files,
            timeout=120
        )

        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }

        else:
            detail = "Unknown error"

            try:
                detail = response.json().get(
                    "detail", detail
                )
            except Exception:
                pass

            return {
                "success": False,
                "error": f"Server error ({response.status_code}): {detail}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Unable to connect to the detection server. Please ensure FastAPI is running."
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Image processing timed out. Please try again."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }


# ============================================================
# UPLOAD VIDEO FOR PREDICTION
# ============================================================

def upload_video(video_bytes, filename):
    """
    Send a video to FastAPI for defect detection,
    tracking, analysis, and QC report generation.

    Args:
        video_bytes: Raw bytes of the video file.
        filename: Original filename (e.g., 'fabric_roll.mp4').

    Returns:
        dict: API response with video info, summary,
              defects list, and report URLs.
        None: On failure.
    """
    try:
        files = {
            "video": (
                filename,
                video_bytes,
                _get_video_content_type(filename)
            )
        }

        response = requests.post(
            f"{API_BASE_URL}/predict",
            files=files,
            timeout=600
        )

        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }

        else:
            detail = "Unknown error"

            try:
                detail = response.json().get(
                    "detail", detail
                )
            except Exception:
                pass

            return {
                "success": False,
                "error": f"Server error ({response.status_code}): {detail}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Unable to connect to the detection server. Please ensure FastAPI is running."
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Video processing timed out. The video may be too large. Please try a shorter clip."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }


# ============================================================
# FETCH ANNOTATED IMAGE
# ============================================================

def fetch_annotated_image(annotated_path):
    """
    Retrieve the annotated image (with bounding boxes)
    from FastAPI.

    Args:
        annotated_path: Relative path returned by API
                        (e.g., '/report/<id>/image').

    Returns:
        bytes: Image bytes on success.
        None: On failure.
    """
    try:
        if annotated_path.startswith("http://") or annotated_path.startswith("https://"):
            url = annotated_path
        else:
            url = f"{API_BASE_URL}{annotated_path}"

        response = requests.get(
            url,
            timeout=30
        )

        if response.status_code == 200:
            return response.content

        return None

    except Exception:
        return None


# ============================================================
# FETCH PDF REPORT
# ============================================================

def fetch_pdf_report(report_id):
    """
    Download the PDF QC report from FastAPI.

    Args:
        report_id: The UUID hex string identifying the report.

    Returns:
        bytes: PDF file bytes on success.
        None: On failure.
    """
    try:
        url = f"{API_BASE_URL}/report/{report_id}/pdf"

        response = requests.get(
            url,
            timeout=30
        )

        if response.status_code == 200:
            return response.content

        return None

    except Exception:
        return None


# ============================================================
# UPLOAD PRINT INSPECTION (Reference + Factory)
# ============================================================

def upload_print_inspection(
    reference_bytes,
    reference_filename,
    factory_bytes,
    factory_filename
):
    """
    Send reference and factory images to FastAPI
    for print comparison inspection.

    Args:
        reference_bytes: Raw bytes of the reference image.
        reference_filename: Original filename of reference.
        factory_bytes: Raw bytes of the factory image.
        factory_filename: Original filename of factory image.

    Returns:
        dict: API response with defects, annotated image,
              PDF url, and inspection status.
    """
    try:
        files = {
            "reference_image": (
                reference_filename,
                reference_bytes,
                _get_image_content_type(reference_filename)
            ),
            "factory_image": (
                factory_filename,
                factory_bytes,
                _get_image_content_type(factory_filename)
            )
        }

        response = requests.post(
            f"{API_BASE_URL}/predict/print-inspection",
            files=files,
            timeout=120
        )

        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }

        else:
            detail = "Unknown error"

            try:
                detail = response.json().get(
                    "detail", detail
                )
            except Exception:
                pass

            return {
                "success": False,
                "error": f"Server error ({response.status_code}): {detail}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Unable to connect to the detection server. Please ensure FastAPI is running."
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Print inspection timed out. Please try again."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }


# ============================================================
# HELPER: CONTENT TYPE DETECTION
# ============================================================

def _get_image_content_type(filename):
    """Determine MIME type for image files."""

    lower = filename.lower()

    if lower.endswith(".png"):
        return "image/png"

    if lower.endswith(".jpeg") or lower.endswith(".jpg"):
        return "image/jpeg"

    return "application/octet-stream"


def _get_video_content_type(filename):
    """Determine MIME type for video files."""

    lower = filename.lower()

    if lower.endswith(".mp4"):
        return "video/mp4"

    if lower.endswith(".avi"):
        return "video/x-msvideo"

    if lower.endswith(".mov"):
        return "video/quicktime"

    if lower.endswith(".mkv"):
        return "video/x-matroska"

    if lower.endswith(".webm"):
        return "video/webm"

    return "application/octet-stream"
