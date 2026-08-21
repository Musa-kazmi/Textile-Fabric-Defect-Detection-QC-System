"""
UI Components for Textile Fabric Defect Detection & QC System
==============================================================
Custom CSS styling, metric cards, defect tables,
status badges, and layout helpers for the Streamlit app.
Industrial dark-mode theme.

All visual components use NATIVE Streamlit widgets
(st.metric, st.dataframe, st.columns) instead of raw HTML.
"""

import streamlit as st
import pandas as pd


# ============================================================
# MAIN CSS THEME
# ============================================================

def apply_custom_css():
    """Inject the industrial CSS theme with adaptive light and dark mode support."""

    st.markdown("""
    <style>
        /* ======================================================
           GOOGLE FONT
        ====================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        /* ======================================================
           ROOT VARIABLES (ADAPTIVE THEME)
        ====================================================== */
        :root {
            --bg-card: rgba(30, 41, 59, 0.7);
            --bg-card-hover: rgba(38, 51, 73, 0.9);
            --border-color: rgba(148, 163, 184, 0.25);
            --border-accent: #0e7490;
            --text-primary: inherit;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-cyan: #06b6d4;
            --accent-cyan-dim: #0e7490;
            --accent-cyan-glow: rgba(6, 182, 212, 0.15);
            --success-green: #10b981;
            --success-bg: rgba(16, 185, 129, 0.12);
            --warning-amber: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.12);
            --danger-red: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.12);
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Support for Light Theme */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-card: #f8fafc;
                --bg-card-hover: #f1f5f9;
                --border-color: #cbd5e1;
                --text-secondary: #475569;
                --text-muted: #64748b;
            }
        }

        /* ======================================================
           GLOBAL STYLES
        ====================================================== */
        .stApp {
            font-family: var(--font-family) !important;
        }

        .main .block-container {
            max-width: 1200px;
            padding-top: 1rem;
            padding-bottom: 4rem;
        }

        /* ======================================================
           HEADER
        ====================================================== */
        .main-header {
            text-align: center;
            padding: 1.5rem 1rem 1.25rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }

        .main-header h1 {
            font-family: var(--font-family) !important;
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            margin: 0 0 0.35rem 0;
        }

        .main-header .subtitle {
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        /* ======================================================
           STATUS INDICATOR
        ====================================================== */
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
        }

        .status-dot.online {
            background-color: var(--success-green);
            box-shadow: 0 0 6px var(--success-green);
        }

        .status-dot.offline {
            background-color: var(--danger-red);
            box-shadow: 0 0 6px var(--danger-red);
        }

        .status-text {
            font-size: 0.75rem;
            color: var(--text-muted);
            vertical-align: middle;
        }

        /* ======================================================
           MODE SELECTION CARDS
        ====================================================== */
        .mode-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.75rem 1.25rem;
            text-align: center;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .mode-card:hover {
            border-color: var(--accent-cyan);
            background: var(--bg-card-hover);
            transform: translateY(-2px);
        }

        .mode-card .mode-icon {
            font-size: 2rem;
            margin-bottom: 0.75rem;
        }

        .mode-card .mode-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }

        .mode-card .mode-desc {
            font-size: 0.8rem;
            color: var(--text-secondary);
            line-height: 1.4;
        }

        /* ======================================================
           SECTION HEADERS
        ====================================================== */
        .section-header {
            font-family: var(--font-family) !important;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding-bottom: 0.6rem;
            margin-bottom: 1rem;
            margin-top: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }

        /* ======================================================
           INSPECTION STATUS BADGE
        ====================================================== */
        .inspection-badge {
            display: inline-block;
            padding: 0.4rem 1rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        .inspection-badge.pass {
            background: var(--success-bg);
            color: var(--success-green);
            border: 1px solid var(--success-green);
        }

        .inspection-badge.fail {
            background: var(--danger-bg);
            color: var(--danger-red);
            border: 1px solid var(--danger-red);
        }

        .inspection-badge.warning {
            background: var(--warning-bg);
            color: var(--warning-amber);
            border: 1px solid var(--warning-amber);
        }

        /* ======================================================
           DEFECT SUMMARY LIST
        ====================================================== */
        .defect-summary-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.6rem 0;
            border-bottom: 1px solid var(--border-color);
        }

        .defect-summary-item:last-child {
            border-bottom: none;
        }

        .defect-summary-item .defect-name {
            font-size: 0.85rem;
            font-weight: 500;
        }

        .defect-summary-item .defect-count {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--accent-cyan);
            background: var(--accent-cyan-glow);
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
        }

        /* ======================================================
           STREAMLIT METRIC STYLING
        ====================================================== */
        [data-testid="stMetric"] {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem 1.25rem;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
            font-weight: 500 !important;
            color: var(--text-muted) !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
        }

        /* ======================================================
           DATAFRAME STYLING
        ====================================================== */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }

        /* ======================================================
           DOWNLOAD BUTTON STYLING
        ====================================================== */
        .stDownloadButton > button {
            background-color: var(--accent-cyan-dim) !important;
            color: white !important;
            border: 1px solid var(--accent-cyan) !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            transition: all 0.2s ease !important;
        }

        .stDownloadButton > button:hover {
            background-color: var(--accent-cyan) !important;
        }

    </style>
    """, unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

def render_header(is_online=False):
    """Render the main application header with connection status."""

    if is_online:
        status_html = (
            '<span class="status-dot online"></span>'
            '<span class="status-text">API Connected</span>'
        )
    else:
        status_html = (
            '<span class="status-dot offline"></span>'
            '<span class="status-text">API Offline</span>'
        )

    st.markdown(f"""
    <div class="main-header">
        <h1>Textile Fabric Defect Detection &amp; QC System</h1>
        <div class="subtitle">Automated Quality Control Inspection</div>
        <div style="margin-top: 0.75rem;">{status_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SECTION HEADER
# ============================================================

def render_section_header(title):
    """Render a styled section header."""

    st.markdown(
        f'<div class="section-header">{title}</div>',
        unsafe_allow_html=True
    )


# ============================================================
# METRIC CARDS ROW (NATIVE STREAMLIT)
# ============================================================

def render_metrics(metrics):
    """
    Render a row of metric cards using native st.metric.

    Args:
        metrics: List of dicts with keys:
                 'label', 'value'.
    """
    cols = st.columns(len(metrics))

    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m["label"],
                value=m["value"]
            )


# ============================================================
# INSPECTION STATUS BADGE
# ============================================================

def render_inspection_badge(total_defects):
    """
    Render a pass/fail/warning inspection badge.

    Args:
        total_defects: Integer count of detected defects.
    """
    if total_defects == 0:
        badge_class = "pass"
        badge_text = "✓ INSPECTION PASSED — No Defects Detected"

    elif total_defects <= 3:
        badge_class = "warning"
        badge_text = f"⚠ MINOR DEFECTS DETECTED — {total_defects} Found"

    else:
        badge_class = "fail"
        badge_text = f"✕ DEFECTS DETECTED — {total_defects} Found"

    st.markdown(
        f'<span class="inspection-badge {badge_class}">'
        f'{badge_text}</span>',
        unsafe_allow_html=True
    )


# ============================================================
# DEFECT SUMMARY LIST
# ============================================================

def render_defect_summary(defect_counts):
    """
    Render the defect class summary with counts.

    Args:
        defect_counts: Dict mapping class name to count.
                       e.g., {"Stain": 5, "Contamination": 2}
    """
    if not defect_counts:
        st.info("No defects detected.")
        return

    items_html = ""

    for name, count in defect_counts.items():
        items_html += f"""
        <div class="defect-summary-item">
            <span class="defect-name">{name}</span>
            <span class="defect-count">{count}</span>
        </div>
        """

    st.markdown(items_html, unsafe_allow_html=True)


# ============================================================
# DEFECT TABLE — IMAGE (NATIVE STREAMLIT DATAFRAME)
# ============================================================

def render_image_defect_table(defects):
    """
    Render the defect detail table for image analysis
    using native st.dataframe.

    Args:
        defects: List of defect dicts from API response.
                 Each has: class_name, confidence, location, box.
    """
    if not defects:
        st.info("🔍 No defects detected in this image.")
        return

    rows = []

    for i, d in enumerate(defects, 1):
        conf = d.get("confidence", 0)
        class_name = d.get("class_name", "Unknown")
        location = d.get("location", "—")
        box = d.get("box", [])

        box_str = (
            ", ".join([str(round(b, 1)) for b in box])
            if box else "—"
        )

        if conf >= 0.7:
            level = "High"
        elif conf >= 0.4:
            level = "Medium"
        else:
            level = "Low"

        rows.append({
            "#": i,
            "Defect Type": class_name,
            "Confidence": f"{conf:.2f}",
            "Level": level,
            "Location": location,
            "Bounding Box": f"[{box_str}]"
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DEFECT TABLE — VIDEO (NATIVE STREAMLIT DATAFRAME)
# ============================================================

def render_video_defect_table(defects):
    """
    Render the defect detail table for video analysis
    using native st.dataframe.

    Args:
        defects: List of tracked defect dicts from API.
                 Each has: defect_id, class, maximum_confidence,
                 location, first_frame, last_frame,
                 confidence_level, observations.
    """
    if not defects:
        st.info("🔍 No defects detected in this video.")
        return

    rows = []

    for d in defects:
        conf = d.get("maximum_confidence", 0)
        defect_id = d.get("defect_id", "—")
        class_name = d.get("class", "Unknown")
        location = d.get("location", "—")
        first_frame = d.get("first_frame", "—")
        last_frame = d.get("last_frame", "—")
        observations = d.get("observations", "—")
        level = d.get("confidence_level", "—")

        rows.append({
            "ID": defect_id,
            "Defect Type": class_name,
            "Max Confidence": f"{conf:.2f}",
            "Level": level,
            "Location": location,
            "First Frame": first_frame,
            "Last Frame": last_frame,
            "Observations": observations
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# VIDEO INFO CARD (NATIVE STREAMLIT METRICS)
# ============================================================

def render_video_info(video_info, filename=None):
    """
    Render video information metrics using native st.metric.

    Args:
        video_info: Dict with fps, width, height,
                    total_frames, duration_seconds.
        filename: Original video filename.
    """
    if filename:
        st.markdown(f"**File:** {filename}")

    fps = video_info.get("fps", "—")
    width = video_info.get("width", "—")
    height = video_info.get("height", "—")
    total_frames = video_info.get("total_frames", "—")

    duration = video_info.get("duration_seconds", 0)

    if isinstance(duration, (int, float)):
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_str = f"{minutes}m {seconds}s"
    else:
        duration_str = "—"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("FPS", fps)

    with col2:
        st.metric("Resolution", f"{width}×{height}")

    with col3:
        st.metric("Total Frames", total_frames)

    with col4:
        st.metric("Duration", duration_str)


# ============================================================
# PROCESSING STATUS MESSAGES
# ============================================================

def get_processing_steps():
    """Return the list of processing step messages for video analysis."""

    return [
        "Processing video...",
        "Detecting defects...",
        "Tracking defects across frames...",
        "Analyzing fabric quality...",
        "Generating QC report...",
    ]
