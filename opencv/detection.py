import cv2


# ============================================================
# MODULE 7
# BETTER DIFFERENCE DETECTION
# ============================================================

def create_difference_mask(
    reference_image,
    factory_image,
    threshold=30
):
    """
    Compare reference and aligned factory grayscale images.

    Black = similar area
    White = significant difference
    """

    # --------------------------------------------------------
    # Reduce small image noise
    # --------------------------------------------------------

    reference_blur = cv2.GaussianBlur(
        reference_image,
        (5, 5),
        0
    )

    factory_blur = cv2.GaussianBlur(
        factory_image,
        (5, 5),
        0
    )

    # --------------------------------------------------------
    # Calculate absolute difference
    # --------------------------------------------------------

    difference = cv2.absdiff(
        reference_blur,
        factory_blur
    )

    # --------------------------------------------------------
    # Convert difference to binary mask
    # --------------------------------------------------------

    _, mask = cv2.threshold(
        difference,
        threshold,
        255,
        cv2.THRESH_BINARY
    )

    # --------------------------------------------------------
    # Morphological cleaning
    # --------------------------------------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    # Remove small isolated noise
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    # Connect nearby difference regions
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    return mask


# ============================================================
# MODULE 8
# FIND DEFECTS AND DRAW BOUNDING BOXES
# ============================================================

def find_defects(
    mask,
    min_area=100
):
    """
    Find significant white regions in a binary mask.

    Returns:
        List of defect dictionaries.
    """

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    defects = []

    for contour in contours:

        area = cv2.contourArea(contour)

        # Ignore very small regions
        if area < min_area:
            continue

        x, y, width, height = cv2.boundingRect(
            contour
        )

        defects.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "area": area
        })

    # Largest defects first
    defects.sort(
        key=lambda defect: defect["area"],
        reverse=True
    )

    return defects


def draw_defect_boxes(
    image,
    defects
):
    """
    Draw red bounding boxes around detected defects.
    """

    result = image.copy()

    for index, defect in enumerate(
        defects,
        start=1
    ):

        x = defect["x"]
        y = defect["y"]
        width = defect["width"]
        height = defect["height"]

        # Draw bounding box
        cv2.rectangle(
            result,
            (x, y),
            (x + width, y + height),
            (0, 0, 255),
            2
        )

        # Label defect number
        cv2.putText(
            result,
            f"Defect {index}",
            (x, max(y - 8, 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA
        )

    return result


# ============================================================
# MODULE 9
# DEFECT COORDINATES AND MEASUREMENTS
# ============================================================

def calculate_defect_measurements(
    defects
):
    """
    Convert detected defects into structured
    measurement information.
    """

    measurements = []

    for index, defect in enumerate(
        defects,
        start=1
    ):

        x = defect["x"]
        y = defect["y"]
        width = defect["width"]
        height = defect["height"]
        area = defect["area"]

        measurements.append({
            "defect_id": index,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "area": round(area, 2)
        })

    return measurements


# ============================================================
# MODULE 10
# OK / DEFECTIVE CLASSIFICATION
# ============================================================

def classify_image(
    defects
):
    """
    Basic image-level classification.

    No detected defect:
        OK

    One or more detected defects:
        DEFECTIVE
    """

    if len(defects) == 0:
        return "OK"

    return "DEFECTIVE"


# ============================================================
# MODULE 7–10 COMPLETE GRAYSCALE PIPELINE
# ============================================================

def detect_print_defects(
    reference_image,
    factory_image,
    valid_mask=None,
    threshold=30,
    min_area=100
):
    """
    Complete grayscale difference-based inspection.

    Steps:
        1. Create difference mask
        2. Apply valid alignment mask
        3. Find defect regions
        4. Calculate measurements
        5. Classify image
    """

    # --------------------------------------------------------
    # Module 7
    # --------------------------------------------------------

    mask = create_difference_mask(
        reference_image,
        factory_image,
        threshold
    )

    # --------------------------------------------------------
    # Ignore invalid alignment/padding regions
    # --------------------------------------------------------

    if valid_mask is not None:

        mask = cv2.bitwise_and(
            mask,
            valid_mask
        )

    # --------------------------------------------------------
    # Module 8
    # --------------------------------------------------------

    defects = find_defects(
        mask,
        min_area
    )

    # --------------------------------------------------------
    # Module 9
    # --------------------------------------------------------

    measurements = calculate_defect_measurements(
        defects
    )

    # --------------------------------------------------------
    # Module 10
    # --------------------------------------------------------

    status = classify_image(
        defects
    )

    return (
        mask,
        defects,
        measurements,
        status
    )


# ============================================================
# MODULE 12
# PRINT-SPECIFIC DETECTION
# ============================================================

def create_print_mask(
    image,
    saturation_threshold=50
):
    """
    Extract colorful/saturated print regions.

    White = possible printed region
    Black = less-saturated region
    """

    # --------------------------------------------------------
    # Convert BGR image to HSV
    # --------------------------------------------------------

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # --------------------------------------------------------
    # Extract saturation channel
    # --------------------------------------------------------

    _, saturation, _ = cv2.split(
        hsv
    )

    # --------------------------------------------------------
    # Threshold saturation
    # --------------------------------------------------------

    _, print_mask = cv2.threshold(
        saturation,
        saturation_threshold,
        255,
        cv2.THRESH_BINARY
    )

    # --------------------------------------------------------
    # Clean mask
    # --------------------------------------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    print_mask = cv2.morphologyEx(
        print_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    print_mask = cv2.morphologyEx(
        print_mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    return print_mask


def create_missing_print_mask(
    reference_image,
    factory_image,
    valid_mask=None,
    saturation_threshold=50
):
    """
    Detect areas where print exists in the reference
    but is missing in the factory image.

    Reference print:
        WHITE

    Factory print:
        WHITE

    Missing print:
        WHITE
    """

    # --------------------------------------------------------
    # Create reference print mask
    # --------------------------------------------------------

    reference_print = create_print_mask(
        reference_image,
        saturation_threshold
    )

    # --------------------------------------------------------
    # Create factory print mask
    # --------------------------------------------------------

    factory_print = create_print_mask(
        factory_image,
        saturation_threshold
    )

    # --------------------------------------------------------
    # Find reference print that is absent in factory
    # --------------------------------------------------------

    missing_print = cv2.bitwise_and(
        reference_print,
        cv2.bitwise_not(factory_print)
    )

    # --------------------------------------------------------
    # Remove invalid alignment areas
    # --------------------------------------------------------

    if valid_mask is not None:

        missing_print = cv2.bitwise_and(
            missing_print,
            valid_mask
        )

    return missing_print


def clean_missing_print_mask(
    mask,
    kernel_size=5
):
    """
    Clean the missing-print mask.
    """

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (kernel_size, kernel_size)
    )

    # Remove small isolated regions
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    # Connect nearby parts
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    return mask


def detect_missing_print(
    reference_image,
    factory_image,
    valid_mask=None,
    saturation_threshold=50,
    min_area=100
):
    """
    Complete Module 12 pipeline.

    Detects regions where:
        print exists in reference
        BUT
        print is absent in factory image.
    """

    # --------------------------------------------------------
    # Create missing-print mask
    # --------------------------------------------------------

    mask = create_missing_print_mask(
        reference_image,
        factory_image,
        valid_mask,
        saturation_threshold
    )

    # --------------------------------------------------------
    # Clean mask
    # --------------------------------------------------------

    mask = clean_missing_print_mask(
        mask
    )

    # --------------------------------------------------------
    # Find defect regions
    # --------------------------------------------------------

    defects = find_defects(
        mask,
        min_area
    )

    # --------------------------------------------------------
    # Calculate measurements
    # --------------------------------------------------------

    measurements = calculate_defect_measurements(
        defects
    )

    # --------------------------------------------------------
    # Classify image
    # --------------------------------------------------------

    status = classify_image(
        defects
    )

    return (
        mask,
        defects,
        measurements,
        status
    )