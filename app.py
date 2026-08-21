"""
Textile Fabric Defect Detection & QC System
=============================================
Main Streamlit Application

"""

import streamlit as st
import time
import sys
import os
from io import BytesIO

# Add src directory to system path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# ============================================================
# PROJECT MODULES
# ============================================================

from src.api_client import (
    check_health,
    upload_image,
    upload_video,
    upload_print_inspection,
    fetch_annotated_image,
    fetch_pdf_report,
    API_BASE_URL
)

from src.ui_components import (
    apply_custom_css,
    render_header,
    render_section_header,
    render_metrics,
    render_inspection_badge,
    render_defect_summary,
    render_image_defect_table,
    render_video_defect_table,
    render_video_info,
    get_processing_steps
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Textile Fabric Defect Detection & QC",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# APPLY THEME
# ============================================================

apply_custom_css()


# ============================================================
# SESSION STATE INIT
# ============================================================

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "dashboard"

if "image_result" not in st.session_state:
    st.session_state.image_result = None

if "video_result" not in st.session_state:
    st.session_state.video_result = None

if "camera_result" not in st.session_state:
    st.session_state.camera_result = None

if "print_inspection_result" not in st.session_state:
    st.session_state.print_inspection_result = None


# ============================================================
# NAVIGATION HELPERS
# ============================================================

def go_to(mode):
    st.session_state.current_mode = mode
    # Clear previous results when switching modes
    if mode == "dashboard":
        st.session_state.image_result = None
        st.session_state.video_result = None
        st.session_state.camera_result = None
        st.session_state.print_inspection_result = None


# ============================================================
# CHECK API CONNECTION
# ============================================================

health = check_health()
is_online = health is not None


# ============================================================
# RENDER HEADER
# ============================================================

render_header(is_online)


# ============================================================
# DASHBOARD VIEW (MODE SELECTION)
# ============================================================

if st.session_state.current_mode == "dashboard":

    st.markdown("")

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">📷</div>
            <div class="mode-title">Upload Image</div>
            <div class="mode-desc">
                Analyze a single fabric image for defects.
                Supports JPG, JPEG, PNG formats.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Select Image Mode",
            key="btn_image",
            use_container_width=True
        ):
            go_to("image")
            st.rerun()

    with col2:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">🎬</div>
            <div class="mode-title">Upload Video</div>
            <div class="mode-desc">
                Analyze fabric inspection video with
                tracking and full QC report.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Select Video Mode",
            key="btn_video",
            use_container_width=True
        ):
            go_to("video")
            st.rerun()

    with col3:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">📹</div>
            <div class="mode-title">Live Camera</div>
            <div class="mode-desc">
                Capture fabric images from your webcam
                for instant defect detection.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Select Camera Mode",
            key="btn_camera",
            use_container_width=True
        ):
            go_to("camera")
            st.rerun()

    with col4:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">🖨️</div>
            <div class="mode-title">Print Inspection</div>
            <div class="mode-desc">
                Compare reference vs factory print
                to detect missing print defects.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Select Print Inspection",
            key="btn_print",
            use_container_width=True
        ):
            go_to("print_inspection")
            st.rerun()

    # --------------------------------------------------------
    # System Info Footer
    # --------------------------------------------------------

    st.markdown("")
    st.markdown("")

    with st.container():
        f1, f2, f3 = st.columns(3)

        with f1:
            st.caption(f"**API Server:** {API_BASE_URL}")
        with f2:
            status_str = "Connected" if is_online else "Disconnected"
            st.caption(f"**Status:** {status_str}")
        with f3:
            st.caption("**Engine:** YOLOv8 + ByteTrack")


# ============================================================
# IMAGE MODE
# ============================================================

elif st.session_state.current_mode == "image":

    # Back button
    if st.button("← Back to Dashboard", key="back_img"):
        go_to("dashboard")
        st.rerun()

    render_section_header("Upload Image for Defect Detection")

    # --------------------------------------------------------
    # File Upload
    # --------------------------------------------------------

    uploaded_image = st.file_uploader(
        "Select a fabric image",
        type=["jpg", "jpeg", "png"],
        key="image_uploader",
        help="Supported formats: JPG, JPEG, PNG"
    )

    if uploaded_image is not None:

        # Preview
        col_preview, col_info = st.columns([2, 1])

        with col_preview:
            st.image(
                uploaded_image,
                caption="Uploaded Image",
                use_container_width=True
            )

        with col_info:
            st.markdown(f"**File:** {uploaded_image.name}")
            st.markdown(f"**Size:** {uploaded_image.size / 1024:.1f} KB")
            st.markdown(f"**Type:** {uploaded_image.type}")

        # Analyze button
        st.markdown("")

        if st.button(
            "🔍  Analyze Image",
            key="analyze_image",
            use_container_width=True,
            type="primary"
        ):
            if not is_online:
                st.error(
                    "Unable to connect to the detection server. "
                    "Please ensure FastAPI is running."
                )
            else:
                # Send to API
                with st.spinner("Analyzing image for defects..."):
                    image_bytes = uploaded_image.getvalue()

                    result = upload_image(
                        image_bytes,
                        uploaded_image.name
                    )

                if result and result["success"]:
                    st.session_state.image_result = result["data"]
                    st.rerun()

                elif result:
                    st.error(result["error"])

                else:
                    st.error(
                        "An unexpected error occurred. "
                        "Please try again."
                    )

    # --------------------------------------------------------
    # Image Results
    # --------------------------------------------------------

    if st.session_state.image_result is not None:

        data = st.session_state.image_result

        st.markdown("---")

        render_section_header("QC Inspection Result")

        summary = data.get("summary", {})
        defects = data.get("defects", [])
        report_id = data.get("report_id", "")
        annotated_path = data.get("annotated_image", "")

        total = summary.get("total_defects", len(defects))
        unique = summary.get("total_unique_defects", 0)
        most_common = summary.get("most_common_defect", "—")

        # Inspection badge
        render_inspection_badge(total)

        st.markdown("")

        # Metrics row
        render_metrics([
            {
                "label": "Total Defects",
                "value": total,
                "color": "red" if total > 3 else (
                    "amber" if total > 0 else "green"
                )
            },
            {
                "label": "Unique Defect Types",
                "value": unique,
                "color": "cyan"
            },
            {
                "label": "Most Common",
                "value": most_common if most_common else "—"
            },
        ])

        # Annotated image
        if annotated_path:
            render_section_header("Detection Result — Annotated Image")

            annotated_bytes = fetch_annotated_image(annotated_path)

            if annotated_bytes:
                st.image(
                    annotated_bytes,
                    caption="Detected Defects (Bounding Boxes)",
                    use_container_width=True
                )
            else:
                st.warning("Could not load annotated image from server.")

        # Defect summary breakdown
        defect_counts = summary.get("defect_counts", {})

        if defect_counts:
            render_section_header("Defect Summary")
            render_defect_summary(defect_counts)

        # Defect table
        render_section_header("Defect Detail Table")
        render_image_defect_table(defects)

        # PDF Download
        st.markdown("")
        st.markdown("")

        if report_id:
            pdf_bytes = fetch_pdf_report(report_id)

            if pdf_bytes:
                st.download_button(
                    label="📄  Download PDF QC Report",
                    data=pdf_bytes,
                    file_name=f"QC_Report_{report_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning(
                    "PDF report is not available. "
                    "The server may still be generating it."
                )


# ============================================================
# VIDEO MODE
# ============================================================

elif st.session_state.current_mode == "video":

    # Back button
    if st.button("← Back to Dashboard", key="back_vid"):
        go_to("dashboard")
        st.rerun()

    render_section_header("Upload Video for Defect Detection & QC Report")

    # --------------------------------------------------------
    # File Upload
    # --------------------------------------------------------

    uploaded_video = st.file_uploader(
        "Select a fabric inspection video",
        type=["mp4", "avi", "mov", "mkv"],
        key="video_uploader",
        help="Supported formats: MP4, AVI, MOV, MKV"
    )

    if uploaded_video is not None:

        # Preview info
        st.markdown(
            f"**File:** {uploaded_video.name}  |  "
            f"**Size:** {uploaded_video.size / (1024 * 1024):.1f} MB"
        )

        # Video preview
        st.video(uploaded_video)

        # Analyze button
        st.markdown("")

        if st.button(
            "🔍  Analyze Video",
            key="analyze_video",
            use_container_width=True,
            type="primary"
        ):
            if not is_online:
                st.error(
                    "Unable to connect to the detection server. "
                    "Please ensure FastAPI is running."
                )
            else:
                # Processing status display
                status_placeholder = st.empty()
                progress_bar = st.progress(0)
                steps = get_processing_steps()

                # Show processing steps
                for i, step_msg in enumerate(steps):
                    status_placeholder.info(f"⏳ {step_msg}")
                    progress_bar.progress(
                        (i + 1) / (len(steps) + 1)
                    )
                    time.sleep(0.6)

                # Actual API call
                status_placeholder.info(
                    "⏳ Waiting for server response..."
                )

                video_bytes = uploaded_video.getvalue()

                result = upload_video(
                    video_bytes,
                    uploaded_video.name
                )

                progress_bar.progress(1.0)

                if result and result["success"]:
                    status_placeholder.success(
                        "✅ Analysis complete!"
                    )
                    time.sleep(0.5)
                    status_placeholder.empty()
                    progress_bar.empty()

                    st.session_state.video_result = {
                        "data": result["data"],
                        "filename": uploaded_video.name
                    }
                    st.rerun()

                elif result:
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.error(result["error"])

                else:
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.error(
                        "Video processing failed. "
                        "Please try again."
                    )

    # --------------------------------------------------------
    # Video Results
    # --------------------------------------------------------

    if st.session_state.video_result is not None:

        vr = st.session_state.video_result
        data = vr["data"]
        filename = vr.get("filename", "—")

        st.markdown("---")

        render_section_header("QC Inspection Result")

        summary = data.get("summary", {})
        defects = data.get("defects", [])
        video_info = data.get("video", {})
        report_id = data.get("report_id", "")
        reports = data.get("reports", {})

        total = summary.get(
            "total_unique_defects",
            len(defects)
        )
        most_common = summary.get("most_common_defect", "—")

        # Inspection badge
        render_inspection_badge(total)

        st.markdown("")

        # Video information
        render_section_header("Video Information")
        render_video_info(video_info, filename)

        # Defect summary metrics
        render_section_header("Defect Summary")

        defect_counts = summary.get("defect_counts", {})

        if defect_counts:
            # Summary metrics row
            render_metrics([
                {
                    "label": "Total Unique Defects",
                    "value": total,
                    "color": "red" if total > 3 else (
                        "amber" if total > 0 else "green"
                    )
                },
                {
                    "label": "Most Common Defect",
                    "value": most_common if most_common else "—",
                    "color": "cyan"
                },
                {
                    "label": "Defect Classes",
                    "value": len(defect_counts),
                    "color": "cyan"
                },
            ])

            # Defect class breakdown
            render_defect_summary(defect_counts)

        else:
            st.info("No defects detected in this video.")

        # Defect detail table
        render_section_header("Defect Detail Table")
        render_video_defect_table(defects)

        # PDF Download
        st.markdown("")
        st.markdown("")

        if report_id:
            pdf_bytes = fetch_pdf_report(report_id)

            if pdf_bytes:
                st.download_button(
                    label="📄  Download PDF QC Report",
                    data=pdf_bytes,
                    file_name=f"QC_Report_{report_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning(
                    "PDF report is not available. "
                    "The server may still be generating it."
                )


# ============================================================
# LIVE CAMERA MODE
# ============================================================

elif st.session_state.current_mode == "camera":

    # Back button
    if st.button("← Back to Dashboard", key="back_cam"):
        go_to("dashboard")
        st.rerun()

    render_section_header("Live Camera — Capture & Analyze")

    st.caption(
        "Capture live images or video recordings from your webcam for instant quality control analysis."
    )

    # --------------------------------------------------------
    # Camera Sub-mode Selection (Image vs Video)
    # --------------------------------------------------------

    cam_tab1, cam_tab2 = st.tabs(["📷  Live Camera Image", "🎥  Live Camera Video"])

    with cam_tab1:
        camera_image = st.camera_input(
            "Capture a fabric image",
            key="camera_image_input"
        )

        if camera_image is not None:
            st.markdown("")

            if st.button(
                "🔍  Analyze Captured Image",
                key="analyze_camera_image",
                use_container_width=True,
                type="primary"
            ):
                if not is_online:
                    st.error(
                        "Unable to connect to the detection server. "
                        "Please ensure FastAPI is running."
                    )
                else:
                    with st.spinner(
                        "Analyzing captured image for defects..."
                    ):
                        image_bytes = camera_image.getvalue()

                        result = upload_image(
                            image_bytes,
                            "camera_capture.jpg"
                        )

                    if result and result["success"]:
                        st.session_state.camera_result = {
                            "type": "image",
                            "data": result["data"]
                        }
                        st.rerun()

                    elif result:
                        st.error(result["error"])

                    else:
                        st.error(
                            "An unexpected error occurred. "
                            "Please try again."
                        )

    with cam_tab2:
        st.caption(
            "Use the live camera recorder below to record fabric moving on your conveyor/inspection line. Once recorded, click 'Analyze Recorded Video' to test directly."
        )

        import streamlit.components.v1 as components
        import base64

        component_path = os.path.join(os.path.dirname(__file__), "src", "camera_component")
        live_video_recorder = components.declare_component("live_video_recorder", path=component_path)

        recorded_base64 = live_video_recorder(key="camera_video_recorder_component", default=None, height=520)

        if recorded_base64:
            if not is_online:
                st.error(
                    "Unable to connect to the detection server. "
                    "Please ensure FastAPI is running."
                )
            else:
                status_placeholder = st.empty()
                progress_bar = st.progress(0)
                steps = get_processing_steps()

                for i, step_msg in enumerate(steps):
                    status_placeholder.info(f"⏳ {step_msg}")
                    progress_bar.progress((i + 1) / (len(steps) + 1))
                    time.sleep(0.5)

                status_placeholder.info("⏳ Processing recorded live video on FastAPI server...")

                try:
                    if "," in recorded_base64:
                        _, encoded = recorded_base64.split(",", 1)
                    else:
                        encoded = recorded_base64

                    video_bytes = base64.b64decode(encoded)

                    result = upload_video(
                        video_bytes,
                        "live_camera_recording.webm"
                    )

                    progress_bar.progress(1.0)

                    if result and result["success"]:
                        status_placeholder.success("✅ Analysis complete!")
                        time.sleep(0.5)
                        status_placeholder.empty()
                        progress_bar.empty()

                        st.session_state.camera_result = {
                            "type": "video",
                            "data": result["data"],
                            "filename": "live_camera_recording.webm"
                        }
                        st.rerun()

                    elif result:
                        status_placeholder.empty()
                        progress_bar.empty()
                        st.error(result["error"])

                    else:
                        status_placeholder.empty()
                        progress_bar.empty()
                        st.error("Camera video processing failed. Please try again.")

                except Exception as ex:
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.error(f"Error processing video stream: {str(ex)}")



    # --------------------------------------------------------
    # Camera Results
    # --------------------------------------------------------

    if st.session_state.camera_result is not None:

        cam_res = st.session_state.camera_result
        res_type = cam_res.get("type", "image")

        if isinstance(cam_res, dict) and "data" in cam_res:
            data = cam_res["data"]
            filename = cam_res.get("filename", "camera_recording.mp4")
        else:
            data = cam_res
            res_type = "image"
            filename = "camera_capture.jpg"

        st.markdown("---")

        render_section_header("QC Inspection Result")

        summary = data.get("summary", {})
        defects = data.get("defects", [])
        report_id = data.get("report_id", "")

        if res_type == "video":
            video_info = data.get("video", {})
            total = summary.get("total_unique_defects", len(defects))
            most_common = summary.get("most_common_defect", "—")

            render_inspection_badge(total)
            st.markdown("")

            render_section_header("Camera Video Information")
            render_video_info(video_info, filename)

            render_section_header("Defect Summary")
            defect_counts = summary.get("defect_counts", {})

            if defect_counts:
                render_metrics([
                    {
                        "label": "Total Unique Defects",
                        "value": total,
                        "color": "red" if total > 3 else ("amber" if total > 0 else "green")
                    },
                    {
                        "label": "Most Common Defect",
                        "value": most_common if most_common else "—",
                        "color": "cyan"
                    },
                    {
                        "label": "Defect Classes",
                        "value": len(defect_counts),
                        "color": "cyan"
                    },
                ])

                render_defect_summary(defect_counts)

            else:
                st.info("No defects detected in camera video.")

            render_section_header("Defect Detail Table")
            render_video_defect_table(defects)

        else:
            annotated_path = data.get("annotated_image", "")
            total = summary.get("total_defects", len(defects))
            unique = summary.get("total_unique_defects", 0)
            most_common = summary.get("most_common_defect", "—")

            render_inspection_badge(total)
            st.markdown("")

            render_metrics([
                {
                    "label": "Total Defects",
                    "value": total,
                    "color": "red" if total > 3 else ("amber" if total > 0 else "green")
                },
                {
                    "label": "Unique Defect Types",
                    "value": unique,
                    "color": "cyan"
                },
                {
                    "label": "Most Common",
                    "value": most_common if most_common else "—"
                },
            ])

            if annotated_path:
                render_section_header("Detection Result — Annotated Image")

                annotated_bytes = fetch_annotated_image(annotated_path)

                if annotated_bytes:
                    st.image(
                        annotated_bytes,
                        caption="Detected Defects (Bounding Boxes)",
                        use_container_width=True
                    )
                else:
                    st.warning("Could not load annotated image from server.")

            defect_counts = summary.get("defect_counts", {})

            if defect_counts:
                render_section_header("Defect Summary")
                render_defect_summary(defect_counts)

            render_section_header("Defect Detail Table")
            render_image_defect_table(defects)

        # PDF Download
        st.markdown("")
        st.markdown("")

        if report_id:
            pdf_bytes = fetch_pdf_report(report_id)

            if pdf_bytes:
                st.download_button(
                    label="📄  Download PDF QC Report",
                    data=pdf_bytes,
                    file_name=f"QC_Report_{report_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning(
                    "PDF report is not available. "
                    "The server may still be generating it."
                )


# ============================================================
# PRINT INSPECTION MODE
# ============================================================

elif st.session_state.current_mode == "print_inspection":

    # Back button
    if st.button("← Back to Dashboard", key="back_print"):
        go_to("dashboard")
        st.rerun()

    render_section_header("Print Inspection — Reference vs Factory Comparison")

    st.caption(
        "Upload the **reference image** (correct expected print) and the "
        "**factory image** (manufactured product). The system will compare "
        "both images and detect missing or defective print areas."
    )

    # --------------------------------------------------------
    # Two Image Uploaders Side-by-Side
    # --------------------------------------------------------

    col_ref, col_fac = st.columns(2, gap="large")

    with col_ref:
        st.markdown("#### 📐 Reference Image")
        st.caption("The correct/expected print design")

        reference_image = st.file_uploader(
            "Upload reference image",
            type=["jpg", "jpeg", "png"],
            key="print_reference_uploader",
            help="Upload the correct print design image"
        )

        if reference_image is not None:
            st.image(
                reference_image,
                caption="Reference (Expected Design)",
                use_container_width=True
            )
            st.markdown(
                f"**File:** {reference_image.name}  |  "
                f"**Size:** {reference_image.size / 1024:.1f} KB"
            )

    with col_fac:
        st.markdown("#### 🏭 Factory Image")
        st.caption("The actual manufactured product")

        factory_image = st.file_uploader(
            "Upload factory image",
            type=["jpg", "jpeg", "png"],
            key="print_factory_uploader",
            help="Upload the manufactured/factory product image"
        )

        if factory_image is not None:
            st.image(
                factory_image,
                caption="Factory (Manufactured Product)",
                use_container_width=True
            )
            st.markdown(
                f"**File:** {factory_image.name}  |  "
                f"**Size:** {factory_image.size / 1024:.1f} KB"
            )

    # --------------------------------------------------------
    # Analyze Button
    # --------------------------------------------------------

    st.markdown("")

    if reference_image is not None and factory_image is not None:

        if st.button(
            "🔍  Analyze Print Inspection",
            key="analyze_print",
            use_container_width=True,
            type="primary"
        ):
            if not is_online:
                st.error(
                    "Unable to connect to the detection server. "
                    "Please ensure FastAPI is running."
                )
            else:
                status_placeholder = st.empty()
                progress_bar = st.progress(0)

                steps = [
                    "Loading reference image...",
                    "Loading factory image...",
                    "Preprocessing and aligning images...",
                    "Detecting missing print defects...",
                    "Analyzing defect regions...",
                    "Generating QC report..."
                ]

                for i, step_msg in enumerate(steps):
                    status_placeholder.info(f"⏳ {step_msg}")
                    progress_bar.progress(
                        (i + 1) / (len(steps) + 1)
                    )
                    time.sleep(0.5)

                status_placeholder.info(
                    "⏳ Waiting for server response..."
                )

                ref_bytes = reference_image.getvalue()
                fac_bytes = factory_image.getvalue()

                result = upload_print_inspection(
                    ref_bytes,
                    reference_image.name,
                    fac_bytes,
                    factory_image.name
                )

                progress_bar.progress(1.0)

                if result and result["success"]:
                    status_placeholder.success(
                        "✅ Print inspection complete!"
                    )
                    time.sleep(0.5)
                    status_placeholder.empty()
                    progress_bar.empty()

                    st.session_state.print_inspection_result = (
                        result["data"]
                    )
                    st.rerun()

                elif result:
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.error(result["error"])

                else:
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.error(
                        "Print inspection failed. "
                        "Please try again."
                    )

    elif reference_image is None or factory_image is None:
        st.info(
            "Please upload both the **reference** and "
            "**factory** images to start inspection."
        )

    # --------------------------------------------------------
    # Print Inspection Results
    # --------------------------------------------------------

    if st.session_state.print_inspection_result is not None:

        data = st.session_state.print_inspection_result

        st.markdown("---")

        render_section_header("Print Inspection — QC Result")

        status = data.get("status", "UNKNOWN")
        total_defects = data.get("total_defects", 0)
        defects = data.get("defects", [])
        report_id = data.get("report_id", "")
        annotated_url = data.get("annotated_image_url", "")

        # Inspection badge
        render_inspection_badge(total_defects)

        st.markdown("")

        # Metrics row
        render_metrics([
            {
                "label": "Inspection Status",
                "value": status,
                "color": "green" if status == "PASS" else "red"
            },
            {
                "label": "Total Defects",
                "value": total_defects,
                "color": "red" if total_defects > 3 else (
                    "amber" if total_defects > 0 else "green"
                )
            },
            {
                "label": "Inspection Type",
                "value": "Print Comparison",
                "color": "cyan"
            },
        ])

        # Annotated image
        if annotated_url or report_id:
            render_section_header(
                "Detection Result — Annotated Image"
            )

            annotated_target = annotated_url if annotated_url else f"/report/{report_id}/image"
            annotated_bytes = fetch_annotated_image(annotated_target)

            if annotated_bytes:
                st.image(
                    annotated_bytes,
                    caption="Detected Print Defects (Bounding Boxes)",
                    use_container_width=True
                )
            else:
                # Local fallback check
                local_img = os.path.join("reports", f"{report_id}_annotated.jpg")
                if os.path.exists(local_img):
                    st.image(
                        local_img,
                        caption="Detected Print Defects (Bounding Boxes)",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "Could not load annotated image from server."
                    )

        # Defect detail table
        render_section_header("Defect Detail Table")

        if defects:
            import pandas as pd

            table_data = []

            for i, d in enumerate(defects, 1):
                table_data.append({
                    "#": i,
                    "Defect Type": d.get(
                        "defect_type", "missing_print"
                    ),
                    "Confidence": f"{d.get('confidence', 0):.0%}",
                    "Bounding Box": str(
                        d.get("box_2d", "—")
                    ),
                    "Description": d.get(
                        "description", "—"
                    )
                })

            df = pd.DataFrame(table_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "🔍 No print defects detected — "
                "factory output matches reference."
            )

        # PDF Download
        st.markdown("")
        st.markdown("")

        if report_id:
            pdf_bytes = fetch_pdf_report(report_id)

            if pdf_bytes:
                st.download_button(
                    label="📄  Download PDF QC Report",
                    data=pdf_bytes,
                    file_name=f"QC_Print_Report_{report_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning(
                    "PDF report is not available. "
                    "The server may still be generating it."
                )
