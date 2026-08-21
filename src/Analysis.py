# ============================================================
# CONFIDENCE CATEGORY
# ============================================================

def get_confidence_level(
    confidence
):

    if confidence >= 0.70:

        return "High"

    elif confidence >= 0.40:

        return "Medium"

    else:

        return "Low"


# ============================================================
# DEFECT SIZE
# ============================================================

def calculate_defect_size(
    defect
):

    boxes = defect.get(
        "boxes",
        []
    )


    if not boxes:

        defect[
            "maximum_box_area_pixels"
        ] = None

        defect[
            "average_box_area_pixels"
        ] = None

        return defect


    areas = []


    for box in boxes:

        x1, y1, x2, y2 = box


        width = max(

            0,

            x2 - x1

        )


        height = max(

            0,

            y2 - y1

        )


        area = (
            width * height
        )


        areas.append(
            area
        )


    defect[
        "maximum_box_area_pixels"
    ] = max(areas)


    defect[
        "average_box_area_pixels"
    ] = (
        sum(areas)
        / len(areas)
    )


    return defect


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_defects(
    tracking_result
):

    video_info = tracking_result[
        "video_info"
    ]


    defects = tracking_result[
        "defects"
    ]


    # ========================================================
    # DEFECT COUNTS
    # ========================================================

    defect_counts = {}


    for defect in defects:

        class_name = defect[
            "class"
        ]


        if class_name not in defect_counts:

            defect_counts[
                class_name
            ] = 0


        defect_counts[
            class_name
        ] += 1


    # ========================================================
    # CONFIDENCE + SIZE
    # ========================================================

    for defect in defects:

        defect[
            "confidence_level"
        ] = get_confidence_level(

            defect[
                "maximum_confidence"
            ]

        )


        calculate_defect_size(
            defect
        )


    # ========================================================
    # MOST COMMON DEFECT
    # ========================================================

    if defect_counts:

        most_common_defect = max(

            defect_counts,

            key=defect_counts.get

        )

    else:

        most_common_defect = None


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    qc_summary = {

        "total_unique_defects":
            len(defects),

        "defect_counts":
            defect_counts,

        "most_common_defect":
            most_common_defect
    }


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    return {

        "video_info":
            video_info,

        "summary":
            qc_summary,

        "defects":
            defects
    }


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_image_defects(
    detection_result
):

    image_info = detection_result[
        "image_info"
    ]

    detections = detection_result[
        "detections"
    ]


    # ========================================================
    # DEFECT COUNTS
    # ========================================================

    defect_counts = {}


    for detection in detections:

        class_name = detection[
            "class_name"
        ]


        if class_name not in defect_counts:

            defect_counts[
                class_name
            ] = 0


        defect_counts[
            class_name
        ] += 1


    # ========================================================
    # ADD CONFIDENCE LEVEL
    # ========================================================

    for detection in detections:

        detection[
            "confidence_level"
        ] = get_confidence_level(

            detection[
                "confidence"
            ]

        )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    most_common_defect = None


    if defect_counts:

        most_common_defect = max(

            defect_counts,

            key=defect_counts.get

        )


    qc_summary = {

    "total_defects":
        len(detections),

    "total_unique_defects":
        len(defect_counts),

    "defect_counts":
        defect_counts,

    "most_common_defect":
        most_common_defect
        }


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    return {

        "image_info":
            image_info,

        "summary":
            qc_summary,

        "defects":
            detections

    }