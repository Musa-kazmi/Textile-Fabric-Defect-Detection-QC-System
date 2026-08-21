import json


class DefectAnalyzer:
    """
    Module 14:
    Analyzes detected printing defects and
    creates structured defect information.
    """

    def __init__(self):
        pass

    def get_location(
        self,
        box,
        image_width=1000,
        image_height=1000
    ):
        """
        Determine approximate location of defect.

        box format:
        [ymin, xmin, ymax, xmax]

        Coordinates are expected on 0-1000 scale.
        """

        ymin, xmin, ymax, xmax = box

        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2

        # Horizontal position
        if center_x < 333:
            horizontal = "left"
        elif center_x < 666:
            horizontal = "center"
        else:
            horizontal = "right"

        # Vertical position
        if center_y < 333:
            vertical = "top"
        elif center_y < 666:
            vertical = "middle"
        else:
            vertical = "bottom"

        return f"{vertical}-{horizontal}"

    def analyze(self, detection_result):
        """
        Analyze the VLM/OpenCV detection result.

        Expected input:

        {
            "defect_detected": true,
            "defects": [
                {
                    "defect_type": "missing_print",
                    "box_2d": [100, 200, 250, 350],
                    "confidence": 0.91,
                    "description": "..."
                }
            ]
        }
        """

        defects = detection_result.get(
            "defects",
            []
        )

        analyzed_defects = []

        for index, defect in enumerate(
            defects,
            start=1
        ):

            box = defect.get(
                "box_2d",
                [0, 0, 0, 0]
            )

            defect_type = defect.get(
                "defect_type",
                "unknown"
            )

            confidence = defect.get(
                "confidence",
                0
            )

            description = defect.get(
                "description",
                ""
            )

            location = self.get_location(
                box
            )

            analyzed_defects.append(
                {
                    "id": index,
                    "type": defect_type,
                    "location": location,
                    "box": box,
                    "confidence": round(
                        float(confidence),
                        3
                    ),
                    "description": description
                }
            )

        # -----------------------------------
        # Overall status
        # -----------------------------------

        total_defects = len(
            analyzed_defects
        )

        if total_defects > 0:
            inspection_status = "DEFECTIVE"
        else:
            inspection_status = "PASS"

        # -----------------------------------
        # Final structured result
        # -----------------------------------

        result = {
            "inspection_status": inspection_status,
            "total_defects": total_defects,
            "defects": analyzed_defects
        }

        return result

    def save_result(
        self,
        result,
        output_path="results/defect_analysis.json"
    ):

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        return output_path


if __name__ == "__main__":

    # Test data
    detection_result = {

        "defect_detected": True,

        "defects": [

            {
                "defect_type": "missing_print",

                "box_2d": [
                    100,
                    600,
                    250,
                    750
                ],

                "confidence": 0.91,

                "description":
                    "Expected print is missing."
            },

            {
                "defect_type": "foreign_spot",

                "box_2d": [
                    700,
                    200,
                    760,
                    260
                ],

                "confidence": 0.94,

                "description":
                    "Unexpected spot detected."
            }
        ]
    }

    analyzer = DefectAnalyzer()

    result = analyzer.analyze(
        detection_result
    )

    print("\n========== DEFECT ANALYSIS ==========\n")

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    analyzer.save_result(result)

    print(
        "\nAnalysis saved to "
        "results/defect_analysis.json"
    )