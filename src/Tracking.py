from collections import defaultdict


# ============================================================
# BUILD QC DATA
# ============================================================

def track_detections(
    detection_result
):

    track_history = detection_result[
        "track_history"
    ]


    video_info = detection_result[
        "video_info"
    ]


    qc_data = []


    # ========================================================
    # PROCESS EACH TRACK
    # ========================================================

    for track_id, history in track_history.items():

        frames = history[
            "frames"
        ]


        timestamps = history[
            "timestamps"
        ]


        confidences = history[
            "confidences"
        ]


        locations = history[
            "locations"
        ]


        boxes = history[
            "boxes"
        ]


        # ----------------------------------------------------
        # Empty track
        # ----------------------------------------------------

        if len(frames) == 0:

            continue


        # ----------------------------------------------------
        # First / Last
        # ----------------------------------------------------

        first_frame = frames[0]

        last_frame = frames[-1]


        first_timestamp = (
            timestamps[0]
        )


        last_timestamp = (
            timestamps[-1]
        )


        # ----------------------------------------------------
        # Duration
        # ----------------------------------------------------

        duration = (

            last_timestamp

            - first_timestamp

        )


        # ----------------------------------------------------
        # Maximum confidence
        # ----------------------------------------------------

        max_confidence = max(
            confidences
        )


        # ----------------------------------------------------
        # Best location
        # ----------------------------------------------------

        location_counts = defaultdict(
            int
        )


        for location in locations:

            location_counts[
                location
            ] += 1


        best_location = max(

            location_counts,

            key=location_counts.get

        )


        # ----------------------------------------------------
        # QC RECORD
        # ----------------------------------------------------

        record = {

            "defect_id":
                f"D{track_id:03d}",

            "track_id":
                int(track_id),

            "class":
                history["class_name"],

            "class_id":
                int(history["class_id"]),

            "first_frame":
                int(first_frame),

            "last_frame":
                int(last_frame),

            "first_seen_seconds":
                round(
                    first_timestamp,
                    2
                ),

            "last_seen_seconds":
                round(
                    last_timestamp,
                    2
                ),

            "duration_seconds":
                round(
                    duration,
                    2
                ),

            "observations":
                len(frames),

            "maximum_confidence":
                round(
                    max_confidence,
                    4
                ),

            "location":
                best_location,

            "boxes":
                boxes
        }


        qc_data.append(
            record
        )


    return {

        "video_info":
            video_info,

        "defects":
            qc_data
    }