from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


class QCReportGenerator:
    """
    Module 15:
    Generates an automatic PDF QC report.
    """

    def __init__(self, output_directory="results"):

        self.output_directory = Path(
            output_directory
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate(
        self,
        analysis_result,
        annotated_image=None
    ):
        """
        Generate PDF QC report.

        analysis_result comes from Module 14.
        """

        pdf_path = (
            self.output_directory /
            "qc_report.pdf"
        )

        # -----------------------------------
        # PDF document
        # -----------------------------------

        document = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        story = []

        # -----------------------------------
        # Report title
        # -----------------------------------

        title = Paragraph(
            "<b>TEXTILE PRINT QUALITY REPORT</b>",
            styles["Title"]
        )

        story.append(title)
        story.append(Spacer(1, 15))

        # -----------------------------------
        # Inspection information
        # -----------------------------------

        inspection_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        status = analysis_result.get(
            "inspection_status",
            "UNKNOWN"
        )

        total_defects = analysis_result.get(
            "total_defects",
            0
        )

        story.append(
            Paragraph(
                f"<b>Inspection Time:</b> "
                f"{inspection_time}",
                styles["Normal"]
            )
        )

        story.append(
            Spacer(1, 8)
        )

        story.append(
            Paragraph(
                f"<b>Inspection Status:</b> "
                f"{status}",
                styles["Normal"]
            )
        )

        story.append(
            Spacer(1, 8)
        )

        story.append(
            Paragraph(
                f"<b>Total Defects:</b> "
                f"{total_defects}",
                styles["Normal"]
            )
        )

        story.append(
            Spacer(1, 20)
        )

        # -----------------------------------
        # Annotated inspection image
        # -----------------------------------

        if annotated_image:

            image_path = Path(
                annotated_image
            )

            if image_path.exists():

                story.append(
                    Paragraph(
                        "<b>Inspection Image</b>",
                        styles["Heading2"]
                    )
                )

                story.append(
                    Spacer(1, 10)
                )

                image = Image(
                    str(image_path)
                )

                # Keep image inside A4 page
                image.drawWidth = 6 * inch
                image.drawHeight = (
                    image.imageHeight /
                    image.imageWidth
                ) * image.drawWidth

                story.append(image)

                story.append(
                    Spacer(1, 20)
                )

        # -----------------------------------
        # Defect details
        # -----------------------------------

        story.append(
            Paragraph(
                "<b>Defect Details</b>",
                styles["Heading2"]
            )
        )

        story.append(
            Spacer(1, 10)
        )

        defects = analysis_result.get(
            "defects",
            []
        )

        if defects:

            table_data = [
                [
                    "ID",
                    "Defect Type",
                    "Location",
                    "Confidence",
                    "Description"
                ]
            ]

            for defect in defects:

                confidence = defect.get(
                    "confidence",
                    0
                )

                confidence = (
                    f"{float(confidence) * 100:.1f}%"
                )

                table_data.append(
                    [
                        str(
                            defect.get(
                                "id",
                                ""
                            )
                        ),

                        defect.get(
                            "type",
                            "Unknown"
                        ),

                        defect.get(
                            "location",
                            "Unknown"
                        ),

                        confidence,

                        defect.get(
                            "description",
                            ""
                        )
                    ]
                )

            table = Table(
                table_data,
                colWidths=[
                    30,
                    90,
                    70,
                    65,
                    180
                ],
                repeatRows=1
            )

            table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.lightgrey
                        ),

                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.black
                        ),

                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold"
                        ),

                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            8
                        ),

                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey
                        ),

                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP"
                        ),

                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),

                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        )
                    ]
                )
            )

            story.append(table)

        else:

            story.append(
                Paragraph(
                    "No printing defects detected.",
                    styles["Normal"]
                )
            )

        story.append(
            Spacer(1, 25)
        )

        # -----------------------------------
        # Final result
        # -----------------------------------

        if status == "DEFECTIVE":

            final_text = (
                "<b>FINAL RESULT: DEFECTIVE</b>"
            )

        else:

            final_text = (
                "<b>FINAL RESULT: PASS</b>"
            )

        story.append(
            Paragraph(
                final_text,
                styles["Heading2"]
            )
        )

        # -----------------------------------
        # Build PDF
        # -----------------------------------

        document.build(story)

        return str(pdf_path)


if __name__ == "__main__":

    # ---------------------------------------
    # Example Module 14 result
    # ---------------------------------------

    analysis_result = {

        "inspection_status":
            "DEFECTIVE",

        "total_defects":
            2,

        "defects": [

            {
                "id": 1,

                "type":
                    "missing_print",

                "location":
                    "top-right",

                "box":
                    [100, 600, 250, 750],

                "confidence":
                    0.91,

                "description":
                    "Expected print is missing."
            },

            {
                "id": 2,

                "type":
                    "foreign_spot",

                "location":
                    "bottom-left",

                "box":
                    [700, 200, 760, 260],

                "confidence":
                    0.94,

                "description":
                    "Unexpected spot detected."
            }
        ]
    }

    generator = QCReportGenerator()

    pdf_path = generator.generate(
        analysis_result
    )

    print(
        "\nQC PDF generated:"
    )

    print(pdf_path)