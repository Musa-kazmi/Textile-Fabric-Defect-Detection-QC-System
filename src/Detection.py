from unittest import result

import cv2
from collections import defaultdict
from ultralytics import YOLO
import os


# ============================================================
# MODEL
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
MODEL_PATH = os.path.join(ROOT_DIR, "best.pt")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, "best.pt")


# ============================================================
# LOAD MODEL
# ============================================================

model = YOLO(MODEL_PATH)

print("YOLOv8 model loaded successfully.")


# ============================================================
# LOCATION FUNCTION
# ============================================================

def get_location(
    center_x,
    center_y,
    width,
    height
):

    # Horizontal position

    if center_x < width / 3:

        horizontal = "Left"

    elif center_x < (2 * width / 3):

        horizontal = "Center"

    else:

        horizontal = "Right"


    # Vertical position

    if center_y < height / 3:

        vertical = "Top"

    elif center_y < (2 * height / 3):

        vertical = "Middle"

    else:

        vertical = "Bottom"


    return f"{vertical}-{horizontal}"


# ============================================================
# VIDEO DETECTION + TRACKING
# ============================================================

def run_detection(
    video_path
):

    # --------------------------------------------------------
    # Open video
    # --------------------------------------------------------

    cap = cv2.VideoCapture(
        video_path
    )


    if not cap.isOpened():

        raise RuntimeError(
            "Could not open video."
        )


    # --------------------------------------------------------
    # Video information
    # --------------------------------------------------------

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )


    print(
        "========================================"
    )

    print(
        "TRACKING ANALYSIS"
    )

    print(
        "========================================"
    )

    print(
        "FPS:",
        fps
    )

    print(
        "Width:",
        width
    )

    print(
        "Height:",
        height
    )

    print(
        "Total Frames:",
        total_frames
    )


    # --------------------------------------------------------
    # Track history
    # --------------------------------------------------------

    track_history = defaultdict(

        lambda: {

            "class_name": None,

            "class_id": None,

            "frames": [],

            "timestamps": [],

            "confidences": [],

            "boxes": [],

            "centers": [],

            "locations": []
        }
    )

    # ========================================================
    # REPRESENTATIVE DEFECT FRAMES
    # One best frame is kept for each tracked defect
    # ========================================================

    representative_frames = {}

    representative_dir = os.path.join(
        os.path.dirname(video_path),
        "defect_frames"
    )

    os.makedirs(
        representative_dir,
        exist_ok=True
        )

    # --------------------------------------------------------
    # Process video
    # --------------------------------------------------------

    frame_number = 0


    while True:

        ret, frame = cap.read()


        if not ret:

            break


        frame_number += 1


        # ----------------------------------------------------
        # YOLO + BYTE TRACK
        # ----------------------------------------------------

        results = model.track(

            source=frame,

            tracker="bytetrack.yaml",

            conf=0.25,

            imgsz=640,

            device="cpu",

            persist=True,

            verbose=False
        )


        result = results[0]


        # ----------------------------------------------------
        # No tracks
        # ----------------------------------------------------

        if result.boxes.id is None:

            continue


        boxes = result.boxes

        # ----------------------------------------------------
        # Create annotated defective frame
        # ----------------------------------------------------

        annotated_frame = result.plot()
        
        # ----------------------------------------------------
        # Track information
        # ----------------------------------------------------

        track_ids = (

            boxes.id

            .int()

            .cpu()

            .tolist()
        )


        class_ids = (

            boxes.cls

            .int()

            .cpu()

            .tolist()
        )


        confidences = (

            boxes.conf

            .cpu()

            .tolist()
        )


        coordinates = (

            boxes.xyxy

            .cpu()

            .tolist()
        )


        # ----------------------------------------------------
        # Process each tracked object
        # ----------------------------------------------------

        for (

            track_id,

            class_id,

            confidence,

            box

        ) in zip(

            track_ids,

            class_ids,

            confidences,

            coordinates

        ):

            class_name = model.names[
                class_id
            ]


            x1, y1, x2, y2 = box


            # Center

            center_x = (
                x1 + x2
            ) / 2


            center_y = (
                y1 + y2
            ) / 2


            # Location

            location = get_location(

                center_x,

                center_y,

                width,

                height
            )


            # Timestamp

            if fps > 0:

                timestamp = (
                    frame_number / fps
                )

            else:

                timestamp = 0


            # History

            history = track_history[
                track_id
            ]


            history["class_name"] = (
                class_name
            )


            history["class_id"] = (
                class_id
            )


            history["frames"].append(
                frame_number
            )


            history["timestamps"].append(
                timestamp
            )


            history["confidences"].append(
                float(confidence)
            )


            history["boxes"].append(

                [

                    float(x1),

                    float(y1),

                    float(x2),

                    float(y2)

                ]

            )


            history["centers"].append(

                [

                    float(center_x),

                    float(center_y)

                ]

            )


            history["locations"].append(
                location
            )

            # ========================================================
            # SAVE BEST DEFECT FRAME
            # ========================================================

            previous_best = representative_frames.get(
                track_id
                )
            

            if (
                previous_best is None
                or float(confidence)> previous_best["confidence"]
                ):

                frame_path = os.path.join(
                    representative_dir,
                    f"track_{track_id}.jpg"
                    )

                cv2.imwrite(
                    frame_path,
                    annotated_frame
                    )

                representative_frames[track_id] = {
                    "track_id": track_id,
                    "frame_number": frame_number,
                    "timestamp": timestamp,
                    "confidence": float(confidence),
                    "class_name": class_name,
                    "location": location,
                    "image_path": frame_path
                    }

    # --------------------------------------------------------
    # Release
    # --------------------------------------------------------

    cap.release()


    # --------------------------------------------------------
    # Return everything required by tracking
    # --------------------------------------------------------

    return {

        "track_history":
            dict(track_history),

        "video_info": {

            "fps":
                fps,

            "width":
                width,

            "height":
                height,

            "total_frames":
                total_frames
        },

        "representative_frames":
        list(
            representative_frames.values()
        )
    }


# ============================================================
# IMAGE DETECTION
# ============================================================

def run_image_detection(
    image_path
):

    # --------------------------------------------------------
    # YOLO IMAGE DETECTION
    # --------------------------------------------------------

    results = model.predict(

        source=image_path,

        conf=0.25,

        imgsz=640,

        device="cpu",

        verbose=False

    )


    result = results[0]

    annotated_image = result.plot()


    # --------------------------------------------------------
    # IMAGE INFORMATION
    # --------------------------------------------------------

    height, width = result.orig_shape


    # --------------------------------------------------------
    # DETECTIONS
    # --------------------------------------------------------

    detections = []


    for box in result.boxes:

        confidence = float(
            box.conf[0]
        )

        class_id = int(
            box.cls[0]
        )

        class_name = model.names[
            class_id
        ]


        x1, y1, x2, y2 = (

            box.xyxy[0]
            .cpu()
            .tolist()

        )


        # ----------------------------------------------------
        # CENTER
        # ----------------------------------------------------

        center_x = (
            x1 + x2
        ) / 2


        center_y = (
            y1 + y2
        ) / 2


        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        location = get_location(

            center_x,

            center_y,

            width,

            height

        )


        # ----------------------------------------------------
        # STORE DETECTION
        # ----------------------------------------------------

        detections.append({

            "class_name":
                class_name,

            "class_id":
                class_id,

            "confidence":
                confidence,

            "box": [

                float(x1),

                float(y1),

                float(x2),

                float(y2)

            ],

            "center": [

                float(center_x),

                float(center_y)

            ],

            "location":
                location

        })


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------


    return {

        "image_info": {

            "width":
                width,

            "height":
                height

        },

        "detections":
            detections,

        "annotated_image":
           annotated_image    

    }