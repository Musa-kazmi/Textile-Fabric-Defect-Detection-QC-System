import json
import os

from datetime import datetime

from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.platypus import Image
from reportlab.lib.units import mm,inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

# ============================================================
# GENERATE REPORTS
# ============================================================

def generate_report(
    qc_data,
    report_id,
    video_name,
    report_dir="reports",
    representative_frames=None
):
    if representative_frames is None:
        representative_frames = []
    
   
    os.makedirs(
        report_dir,
        exist_ok=True
    )


    # ========================================================
    # PATHS
    # ========================================================

    json_path = os.path.join(

        report_dir,

        f"{report_id}.json"
    )


    html_path = os.path.join(

        report_dir,

        f"{report_id}.html"
    )


    pdf_path = os.path.join(

        report_dir,

        f"{report_id}.pdf"
    )


    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    summary = qc_data[
        "summary"
    ]


    defects = qc_data[
        "defects"
    ]


    inspection_time = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    # ========================================================
    # FINAL REPORT DATA
    # ========================================================

    final_report = {

        "report_information": {

            "report_type":
                "Textile Fabric Quality Control Report",

            "video":
                video_name,

            "inspection_time":
                inspection_time
        },

        "summary": {

            "total_unique_defects":
                summary[
                    "total_unique_defects"
                ],

            "most_common_defect":
                summary[
                    "most_common_defect"
                ]
        },

        "defect_counts":
            summary[
                "defect_counts"
            ],

        "defects":
            defects
    }


    # ========================================================
    # SAVE JSON
    # ========================================================

    with open(

        json_path,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            final_report,

            file,

            indent=4
        )


    # ========================================================
    # HTML REPORT
    # ========================================================

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
Textile Fabric QC Report
</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 40px;
}}

h1 {{
    text-align: center;
}}

h2 {{
    margin-top: 30px;
}}

.summary {{
    border: 1px solid #444;
    padding: 15px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}}

th,
td {{
    border: 1px solid #999;
    padding: 8px;
    text-align: left;
}}

th {{
    background-color: #eeeeee;
}}

</style>

</head>

<body>

<h1>
TEXTILE FABRIC QUALITY CONTROL REPORT
</h1>

<div class="summary">

<p>
<b>Video:</b>
{video_name}
</p>

<p>
<b>Inspection Time:</b>
{inspection_time}
</p>

<p>
<b>Total Unique Defects:</b>
{summary["total_unique_defects"]}
</p>

<p>
<b>Most Common Defect:</b>
{summary["most_common_defect"]}
</p>

</div>


<h2>
Defect Summary
</h2>

<table>

<tr>

<th>
Defect Type
</th>

<th>
Count
</th>

</tr>
"""


    for class_name, count in (
        summary[
            "defect_counts"
        ].items()
    ):

        html += f"""

<tr>

<td>
{class_name}
</td>

<td>
{count}
</td>

</tr>

"""


    html += """

</table>


<h2>
Defect Details
</h2>

<table>

<tr>

<th>ID</th>

<th>Class</th>

<th>Confidence</th>

<th>Location</th>

<th>First Seen</th>

<th>Last Seen</th>

<th>Duration</th>

<th>Observations</th>

</tr>
"""


    for defect in defects:

        confidence = float(

            defect.get(
                "maximum_confidence",
                0
            )

        )


        html += f"""

<tr>

<td>
{defect.get("defect_id", "N/A")}
</td>

<td>
{defect.get("class", "N/A")}
</td>

<td>
{confidence * 100:.2f}%
</td>

<td>
{defect.get("location", "N/A")}
</td>

<td>
{defect.get("first_seen_seconds", 0):.2f}s
</td>

<td>
{defect.get("last_seen_seconds", 0):.2f}s
</td>

<td>
{defect.get("duration_seconds", 0):.2f}s
</td>

<td>
{defect.get("observations", 0)}
</td>

</tr>

"""


    html += """

</table>

</body>

</html>
"""


    with open(

        html_path,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(
            html
        )


    # ========================================================
    # PDF
    # ========================================================

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(

        "TitleStyle",

        parent=styles["Title"],

        alignment=TA_CENTER,

        fontSize=20,

        spaceAfter=15
    )


    heading_style = ParagraphStyle(

        "HeadingStyle",

        parent=styles["Heading2"],

        fontSize=14,

        spaceBefore=12,

        spaceAfter=8
    )


    document = SimpleDocTemplate(

        pdf_path,

        pagesize=A4,

        rightMargin=15 * mm,

        leftMargin=15 * mm,

        topMargin=15 * mm,

        bottomMargin=15 * mm
    )


    story = []


    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "TEXTILE FABRIC QUALITY CONTROL REPORT",

            title_style

        )

    )


    story.append(

        Spacer(

            1,

            5 * mm

        )

    )


    # --------------------------------------------------------
    # Inspection Information
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "Inspection Information",

            heading_style

        )

    )


    inspection_table = [

        [
            "Video",
            video_name
        ],

        [
            "Inspection Time",
            inspection_time
        ],

        [
            "Total Unique Defects",

            str(
                summary[
                    "total_unique_defects"
                ]
            )
        ],

        [
            "Most Common Defect",

            str(
                summary[
                    "most_common_defect"
                ]
            )
        ]

    ]


    table = Table(
        inspection_table,
        colWidths=[
            55 * mm,
            115 * mm
        ]
    )


    table.setStyle(

        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                None
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                None
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )

        ])

    )


    story.append(
        table
    )


    story.append(
        Spacer(1, 8 * mm)
    )


    # --------------------------------------------------------
    # Defect Summary
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "Defect Summary",

            heading_style

        )

    )


    summary_table_data = [

        [
            "Defect Type",
            "Count"
        ]

    ]


    for class_name, count in (
        summary[
            "defect_counts"
        ].items()
    ):

        summary_table_data.append(

            [
                class_name,
                str(count)
            ]

        )


    summary_table = Table(
        summary_table_data
    )


    summary_table.setStyle(

        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                None
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )

        ])

    )


    story.append(
        summary_table
    )


    story.append(
        Spacer(1, 8 * mm)
    )


    # ========================================================
    # DETECTED DEFECT FRAMES
    # ========================================================

    story.append(
       Paragraph(
            "Detected Defect Frames",
            heading_style
    )
)

    story.append(
        Spacer(1, 5 * mm)
)


    if representative_frames:

        for frame_data in representative_frames:

            image_path = frame_data.get(
            "image_path"
        )

            if not image_path:
                continue

            if not os.path.exists(
                image_path
        ):
                continue

        # --------------------------------------------
        # Defect information
        # --------------------------------------------

            defect_text = (
                f"<b>Defect:</b> "
                f"{frame_data.get('class', 'N/A')}<br/>"
            
                f"<b>Confidence:</b> "
                f"{float(frame_data.get('confidence', 0)) * 100:.2f}%<br/>"
            
                f"<b>Frame:</b> "
                f"{frame_data.get('frame_number', 'N/A')}<br/>"
            
                f"<b>Time:</b> "
                f"{float(frame_data.get('timestamp', 0)):.2f}s<br/>"
            
                f"<b>Location:</b> "
                f"{frame_data.get('location', 'N/A')}"
                )

            story.append(
                Paragraph(
                    defect_text,
                    styles["Normal"]
                    )
                )

            story.append(
                Spacer(1, 3 * mm)
                )

        # --------------------------------------------
        # Annotated defective frame
        # --------------------------------------------

            defect_image = Image(
                image_path
                )

            defect_image._restrictSize(
                160 * mm,
                100 * mm
                )

            story.append(
                defect_image
                )

            story.append(
                Spacer(1, 8 * mm)
                )

    else:

        story.append(
            Paragraph(
                "No defective frames were detected.",
                styles["Normal"]
            )
        )
    


# --------------------------------------------------------
# Individual Defects
# --------------------------------------------------------

    story.append(
        Paragraph(
            "Individual Defects",
            heading_style
    )
)


    # --------------------------------------------------------
    # Individual Defects
    # --------------------------------------------------------

    story.append(

        Paragraph(

            "Individual Defects",

            heading_style

        )

    )


    defect_table_data = [

        [

            "ID",

            "Class",

            "Confidence",

            "Location",

            "First Seen",

            "Last Seen",

            "Duration",

            "Observations"

        ]

    ]


    for defect in defects:

        defect_table_data.append(

            [

                defect.get(
                    "defect_id",
                    "N/A"
                ),

                defect.get(
                    "class",
                    "N/A"
                ),

                f'{float(defect.get("maximum_confidence", 0)) * 100:.2f}%',

                defect.get(
                    "location",
                    "N/A"
                ),

                f'{defect.get("first_seen_seconds", 0):.2f}s',

                f'{defect.get("last_seen_seconds", 0):.2f}s',

                f'{defect.get("duration_seconds", 0):.2f}s',

                str(
                    defect.get(
                        "observations",
                        0
                    )
                )

            ]

        )


    defect_table = Table(

        defect_table_data,

        repeatRows=1,

        colWidths=[

            15 * mm,

            22 * mm,

            25 * mm,

            30 * mm,

            22 * mm,

            22 * mm,

            22 * mm,

            22 * mm

        ]

    )


    defect_table.setStyle(

        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                None
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )

        ])

    )


    story.append(
        defect_table
    )


    # --------------------------------------------------------
    # Build PDF
    # --------------------------------------------------------

    document.build(
        story
    )


    # ========================================================
    # RETURN REPORT PATHS
    # ========================================================

    return {

        "report_id":
            report_id,

        "json":
            json_path,

        "html":
            html_path,

        "pdf":
            pdf_path
    }


# ============================================================
# IMAGE REPORT
# ============================================================

def generate_image_report(
    qc_data,
    report_id,
    image_filename,
    report_dir,
    annotated_image_path
):

    # ========================================================
    # CREATE REPORT DIRECTORY
    # ========================================================

    os.makedirs(
        report_dir,
        exist_ok=True
    )


    # ========================================================
    # PATHS
    # ========================================================

    pdf_path = os.path.join(

        report_dir,

        f"{report_id}.pdf"

    )


    html_path = os.path.join(

        report_dir,

        f"{report_id}.html"

    )


    json_path = os.path.join(

        report_dir,

        f"{report_id}.json"

    )


    # ========================================================
    # DATA
    # ========================================================

    image_info = qc_data.get(
        "image_info",
        {}
    )


    summary = qc_data.get(
        "summary",
        {}
    )


    defects = qc_data.get(
        "defects",
        []
    )


    inspection_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # ========================================================
    # SUMMARY VALUES
    # ========================================================

    defect_counts = summary.get(

        "defect_counts",

        {}

    )


    total_defects = summary.get(

        "total_defects",

        len(defects)

    )


    total_unique_defects = summary.get(

        "total_unique_defects",

        len(defect_counts)

    )


    most_common_defect = summary.get(

        "most_common_defect"

    )


    # ========================================================
    # REPORT JSON DATA
    # ========================================================

    report_json = {

        "report_id":
            report_id,

        "type":
            "image",

        "image":
            image_filename,

        "inspection_time":
            inspection_time,

        "image_info":
            image_info,

        "summary": {

            "total_defects":
                total_defects,

            "total_unique_defects":
                total_unique_defects,

            "defect_counts":
                defect_counts,

            "most_common_defect":
                most_common_defect

        },

        "defects":
            defects

    }


    # ========================================================
    # SAVE JSON
    # ========================================================

    with open(

        json_path,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            report_json,

            file,

            indent=4

        )


    # ========================================================
    # PDF DOCUMENT
    # ========================================================

    document = SimpleDocTemplate(

        pdf_path,

        pagesize=A4,

        rightMargin=36,

        leftMargin=36,

        topMargin=36,

        bottomMargin=36

    )


    styles = getSampleStyleSheet()


    story = []


    # ========================================================
    # TITLE
    # ========================================================

    title = Paragraph(

        "<b>TEXTILE FABRIC QUALITY CONTROL REPORT</b>",

        styles["Title"]

    )


    story.append(title)

    story.append(
        Spacer(1, 25)
    )


    # ========================================================
    # INSPECTION INFORMATION
    # ========================================================

    story.append(

        Paragraph(

            "<b>Inspection Information</b>",

            styles["Heading2"]

        )

    )


    story.append(
        Spacer(1, 10)
    )


    inspection_data = [

        [
            "Image",
            image_filename
        ],

        [
            "Report ID",
            report_id
        ],

        [
            "Inspection Time",
            inspection_time
        ],

        [
            "Image Width",
            str(
                image_info.get(
                    "width",
                    "N/A"
                )
            )
        ],

        [
            "Image Height",
            str(
                image_info.get(
                    "height",
                    "N/A"
                )
            )
        ],

        [
            "Total Defects",
            str(
                total_defects
            )
        ],

        [
            "Unique Defect Types",
            str(
                total_unique_defects
            )
        ],

        [
            "Most Common Defect",
            str(
                most_common_defect
                if most_common_defect
                else "None"
            )
        ]

    ]


    inspection_table = Table(

        inspection_data,

        colWidths=[

            1.8 * inch,

            4.8 * inch

        ]

    )


    inspection_table.setStyle(

        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
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
                6
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6
            )

        ])

    )


    story.append(
        inspection_table
    )


    story.append(
        Spacer(1, 25)
    )


    # ========================================================
    # ANNOTATED IMAGE
    # ========================================================

    story.append(
        Paragraph(
            "<b>Detected Fabric Image</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 10)
        )

    annotated_image = Image(
        annotated_image_path,
        width=500,
        height=500
        )

    story.append(
        annotated_image
        )

    story.append(
        Spacer(1, 25))


    # ========================================================
    # DEFECT SUMMARY
    # ========================================================

    story.append(

        Paragraph(

            "<b>Defect Summary</b>",

            styles["Heading2"]

        )

    )


    story.append(
        Spacer(1, 10)
    )


    summary_data = [

        [
            "Defect Type",
            "Count"
        ]

    ]


    if defect_counts:

        for class_name, count in defect_counts.items():

            summary_data.append([

                class_name,

                str(count)

            ])

    else:

        summary_data.append([

            "No defect detected",

            "0"

        ])


    summary_table = Table(

        summary_data,

        colWidths=[

            3.5 * inch,

            1.2 * inch

        ]

    )


    summary_table.setStyle(

        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            )

        ])

    )


    story.append(
        summary_table
    )


    story.append(
        Spacer(1, 25)
    )


    # ========================================================
    # INDIVIDUAL IMAGE DEFECTS
    # ========================================================

    story.append(

        Paragraph(

            "<b>Detected Defects</b>",

            styles["Heading2"]

        )

    )


    story.append(
        Spacer(1, 10)
    )


    defect_table_data = [

        [

            "ID",

            "Class",

            "Confidence",

            "Location",

            "Bounding Box"

        ]

    ]


    if defects:

        for index, defect in enumerate(

            defects,

            start=1

        ):

            class_name = defect.get(

                "class_name",

                defect.get(

                    "class",

                    "N/A"

                )

            )


            confidence = defect.get(

                "confidence",

                defect.get(

                    "maximum_confidence",

                    0

                )

            )


            location = defect.get(

                "location",

                "N/A"

            )


            box = defect.get(

                "box",

                None

            )


            if box:

                box_text = (

                    "("

                    + ", ".join(

                        str(
                            round(
                                value,
                                1
                            )
                        )

                        for value in box

                    )

                    + ")"

                )

            else:

                box_text = "N/A"


            defect_table_data.append([

                str(index),

                class_name,

                f"{confidence * 100:.2f}%",

                location,

                box_text

            ])


    else:

        defect_table_data.append([

            "N/A",

            "No defect",

            "0.00%",

            "N/A",

            "N/A"

        ])


    defect_table = Table(

        defect_table_data,

        colWidths=[

            0.4 * inch,

            1.3 * inch,

            1.0 * inch,

            1.2 * inch,

            2.2 * inch

        ],

        repeatRows=1

    )


    defect_table.setStyle(

        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            )

        ])

    )


    story.append(
        defect_table
    )


    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story
    )


    # ========================================================
    # HTML REPORT
    # ========================================================

    defect_rows = ""


    for index, defect in enumerate(

        defects,

        start=1

    ):

        class_name = defect.get(

            "class_name",

            defect.get(
                "class",
                "N/A"
            )

        )


        confidence = defect.get(

            "confidence",

            defect.get(
                "maximum_confidence",
                0
            )

        )


        location = defect.get(

            "location",

            "N/A"

        )


        box = defect.get(

            "box",

            None

        )


        if box:

            box_text = (

                "("

                + ", ".join(

                    str(
                        round(
                            value,
                            1
                        )
                    )

                    for value in box

                )

                + ")"

            )

        else:

            box_text = "N/A"


        defect_rows += f"""

        <tr>

            <td>{index}</td>

            <td>{class_name}</td>

            <td>{confidence * 100:.2f}%</td>

            <td>{location}</td>

            <td>{box_text}</td>

        </tr>

        """


    summary_rows = ""


    for class_name, count in defect_counts.items():

        summary_rows += f"""

        <tr>

            <td>{class_name}</td>

            <td>{count}</td>

        </tr>

        """


    html_content = f"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>Textile Fabric QC Report</title>

<style>

body {{

    font-family: Arial, sans-serif;

    margin: 40px;

}}

h1 {{

    text-align: center;

}}

h2 {{

    margin-top: 30px;

}}

table {{

    border-collapse: collapse;

    width: 100%;

    margin-top: 10px;

}}

th, td {{

    border: 1px solid black;

    padding: 8px;

    text-align: left;

}}

th {{

    background-color: #eeeeee;

}}

</style>

</head>


<body>


<h1>

TEXTILE FABRIC QUALITY CONTROL REPORT

</h1>


<h2>

Inspection Information

</h2>


<table>

<tr>

<th>Field</th>

<th>Value</th>

</tr>


<tr>

<td>Image</td>

<td>{image_filename}</td>

</tr>


<tr>

<td>Report ID</td>

<td>{report_id}</td>

</tr>


<tr>

<td>Inspection Time</td>

<td>{inspection_time}</td>

</tr>


<tr>

<td>Image Width</td>

<td>{image_info.get("width", "N/A")}</td>

</tr>


<tr>

<td>Image Height</td>

<td>{image_info.get("height", "N/A")}</td>

</tr>


<tr>

<td>Total Defects</td>

<td>{total_defects}</td>

</tr>


<tr>

<td>Unique Defect Types</td>

<td>{total_unique_defects}</td>

</tr>


<tr>

<td>Most Common Defect</td>

<td>{most_common_defect or "None"}</td>

</tr>


</table>


<h2>

Defect Summary

</h2>


<table>

<tr>

<th>Defect Type</th>

<th>Count</th>

</tr>

{summary_rows}

</table>


<h2>

Detected Defects

</h2>


<table>

<tr>

<th>ID</th>

<th>Class</th>

<th>Confidence</th>

<th>Location</th>

<th>Bounding Box</th>

</tr>

{defect_rows}

</table>


</body>

</html>

"""


    with open(

        html_path,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(
            html_content
        )


    # ========================================================
    # RETURN REPORT PATHS
    # ========================================================

    return {

        "report_id":
            report_id,

        "pdf":
            pdf_path,

        "html":
            html_path,

        "json":
            json_path

    }    