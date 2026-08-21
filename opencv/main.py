# import cv2

# from final_project.opencv.input import load_images, validate_images
# from final_project.opencv.preprocessing import preprocess_images
# from final_project.opencv.alignment import align_images, apply_transform_color

# from final_project.opencv.detection import (
#     detect_print_defects,
#     detect_missing_print,
#     draw_defect_boxes
# )


# def main():

#     # =========================================================
#     # 1. IMAGE PATHS
#     # =========================================================

#     reference_path = (
#         r"C:\Users\User\Downloads\Textile_fabrics"
#         r"\opencv\dot_print_actual.png"
#     )

#     factory_path = (
#         r"C:\Users\User\Downloads\Textile_fabrics"
#         r"\opencv\dot_print_defected.png"
#     )

#     # =========================================================
#     # 2. LOAD IMAGES
#     # =========================================================

#     reference, factory = load_images(
#         reference_path,
#         factory_path
#     )

#     validate_images(
#         reference,
#         factory
#     )

#     print(
#         f"Reference image: "
#         f"{reference.shape[1]} x {reference.shape[0]}"
#     )

#     print(
#         f"Factory image: "
#         f"{factory.shape[1]} x {factory.shape[0]}"
#     )

#     # =========================================================
#     # 3. PREPROCESS IMAGES
#     # =========================================================

#     (
#         reference_gray,
#         factory_gray,
#         factory_resized_color
#     ) = preprocess_images(
#         reference,
#         factory
#     )

#     # =========================================================
#     # 4. ALIGN FACTORY IMAGE
#     # =========================================================

#     (
#         factory_aligned,
#         valid_mask,
#         transform_info
#     ) = align_images(
#         reference_gray,
#         factory_gray
#     )

#     # =========================================================
#     # 5. CREATE ALIGNED COLOR FACTORY IMAGE
#     # =========================================================

#     height, width = reference_gray.shape[:2]

#     factory_aligned_color = apply_transform_color(
#         factory_resized_color,
#         transform_info,
#         (width, height)
#     )

#     # =========================================================
#     # 6. MODULE 7–10
#     # BASIC PIXEL DIFFERENCE METHOD
#     # =========================================================

#     (
#         difference_mask,
#         difference_defects,
#         difference_measurements,
#         difference_status
#     ) = detect_print_defects(
#         reference_gray,
#         factory_aligned,
#         valid_mask=valid_mask,
#         threshold=30,
#         min_area=100
#     )

#     # =========================================================
#     # 7. MODULE 12
#     # PRINT-SPECIFIC DETECTION
#     # =========================================================

#     (
#         missing_print_mask,
#         missing_print_defects,
#         missing_print_measurements,
#         missing_print_status
#     ) = detect_missing_print(
#         reference,
#         factory_aligned_color,
#         valid_mask=valid_mask,
#         saturation_threshold=50,
#         min_area=100
#     )

#     # =========================================================
#     # 8. DRAW MODULE 12 DEFECT BOXES
#     # =========================================================

#     missing_print_result = draw_defect_boxes(
#         factory_aligned_color,
#         missing_print_defects
#     )

#     # =========================================================
#     # 9. PRINT BASIC DIFFERENCE RESULTS
#     # =========================================================

#     print("\n========================================")
#     print("MODULE 7–10 : PIXEL DIFFERENCE")
#     print("========================================")

#     print(
#         f"Status: {difference_status}"
#     )

#     print(
#         f"Possible differences: "
#         f"{len(difference_defects)}"
#     )

#     for defect in difference_measurements:

#         print(
#             f"Defect {defect['defect_id']}: "
#             f"x={defect['x']}, "
#             f"y={defect['y']}, "
#             f"width={defect['width']}, "
#             f"height={defect['height']}, "
#             f"area={defect['area']}"
#         )

#     # =========================================================
#     # 10. PRINT MODULE 12 RESULTS
#     # =========================================================

#     print("\n========================================")
#     print("MODULE 12 : MISSING PRINT DETECTION")
#     print("========================================")

#     print(
#         f"Status: {missing_print_status}"
#     )

#     print(
#         f"Missing-print defects: "
#         f"{len(missing_print_defects)}"
#     )

#     for defect in missing_print_measurements:

#         print(
#             f"Missing Print {defect['defect_id']}: "
#             f"x={defect['x']}, "
#             f"y={defect['y']}, "
#             f"width={defect['width']}, "
#             f"height={defect['height']}, "
#             f"area={defect['area']}"
#         )

#     # =========================================================
#     # 11. DISPLAY REFERENCE
#     # =========================================================

#     cv2.imshow(
#         "Reference",
#         reference
#     )

#     # =========================================================
#     # 12. DISPLAY ORIGINAL FACTORY
#     # =========================================================

#     cv2.imshow(
#         "Factory Original",
#         factory
#     )

#     # =========================================================
#     # 13. DISPLAY ALIGNED FACTORY
#     # =========================================================

#     cv2.imshow(
#         "Factory Aligned",
#         factory_aligned_color
#     )

#     # =========================================================
#     # 14. MODULE 7–10 MASK
#     # =========================================================

#     cv2.imshow(
#         "Pixel Difference Mask",
#         difference_mask
#     )

#     # =========================================================
#     # 15. MODULE 7–10 RESULT
#     # =========================================================

#     difference_result = draw_defect_boxes(
#         factory_aligned_color,
#         difference_defects
#     )

#     cv2.imshow(
#         "Pixel Difference Defects",
#         difference_result
#     )

#     # =========================================================
#     # 16. MODULE 12 MASK
#     # =========================================================

#     cv2.imshow(
#         "Missing Print Mask",
#         missing_print_mask
#     )

#     # =========================================================
#     # 17. MODULE 12 RESULT
#     # =========================================================

#     cv2.imshow(
#         "Missing Print Defects",
#         missing_print_result
#     )

#     # =========================================================
#     # 18. WAIT
#     # =========================================================

#     print("\nPress any key in an image window to close.")

#     cv2.waitKey(0)

#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()



import os
import cv2

from input import load_images, validate_images
from preprocessing import preprocess_images
from alignment import align_images, apply_transform_color

from detection import (
    detect_print_defects,
    detect_missing_print,
    draw_defect_boxes
)

# Added Module Imports
from defect_analysis import DefectAnalyzer
from qc_reprt import QCReportGenerator


def main():

    # =========================================================
    # 1. IMAGE PATHS
    # =========================================================

    reference_path = (
        r"C:\Users\User\Downloads\Textile_fabrics"
        r"\final_project\opencv\dot_print_actual.png"
    )

    factory_path = (
        r"C:\Users\User\Downloads\Textile_fabrics"
        r"\final_project\opencv\dot_print_defected.png"
    )

    # =========================================================
    # 2. LOAD IMAGES
    # =========================================================

    reference, factory = load_images(
        reference_path,
        factory_path
    )

    validate_images(
        reference,
        factory
    )

    print(
        f"Reference image: "
        f"{reference.shape[1]} x {reference.shape[0]}"
    )

    print(
        f"Factory image: "
        f"{factory.shape[1]} x {factory.shape[0]}"
    )

    # =========================================================
    # 3. PREPROCESS IMAGES
    # =========================================================

    (
        reference_gray,
        factory_gray,
        factory_resized_color
    ) = preprocess_images(
        reference,
        factory
    )

    # =========================================================
    # 4. ALIGN FACTORY IMAGE
    # =========================================================

    (
        factory_aligned,
        valid_mask,
        transform_info
    ) = align_images(
        reference_gray,
        factory_gray
    )

    # =========================================================
    # 5. CREATE ALIGNED COLOR FACTORY IMAGE
    # =========================================================

    height, width = reference_gray.shape[:2]

    factory_aligned_color = apply_transform_color(
        factory_resized_color,
        transform_info,
        (width, height)
    )

    # =========================================================
    # 6. MODULE 7–10
    # BASIC PIXEL DIFFERENCE METHOD
    # =========================================================

    (
        difference_mask,
        difference_defects,
        difference_measurements,
        difference_status
    ) = detect_print_defects(
        reference_gray,
        factory_aligned,
        valid_mask=valid_mask,
        threshold=30,
        min_area=100
    )

    # =========================================================
    # 7. MODULE 12
    # PRINT-SPECIFIC DETECTION
    # =========================================================

    (
        missing_print_mask,
        missing_print_defects,
        missing_print_measurements,
        missing_print_status
    ) = detect_missing_print(
        reference,
        factory_aligned_color,
        valid_mask=valid_mask,
        saturation_threshold=50,
        min_area=100
    )

    # =========================================================
    # 8. DRAW MODULE 12 DEFECT BOXES
    # =========================================================

    missing_print_result = draw_defect_boxes(
        factory_aligned_color,
        missing_print_defects
    )

    # =========================================================
    # 9. PRINT BASIC DIFFERENCE RESULTS
    # =========================================================

    print("\n========================================")
    print("MODULE 7–10 : PIXEL DIFFERENCE")
    print("========================================")

    print(
        f"Status: {difference_status}"
    )

    print(
        f"Possible differences: "
        f"{len(difference_defects)}"
    )

    for defect in difference_measurements:

        print(
            f"Defect {defect['defect_id']}: "
            f"x={defect['x']}, "
            f"y={defect['y']}, "
            f"width={defect['width']}, "
            f"height={defect['height']}, "
            f"area={defect['area']}"
        )

    # =========================================================
    # 10. PRINT MODULE 12 RESULTS
    # =========================================================

    print("\n========================================")
    print("MODULE 12 : MISSING PRINT DETECTION")
    print("========================================")

    print(
        f"Status: {missing_print_status}"
    )

    print(
        f"Missing-print defects: "
        f"{len(missing_print_defects)}"
    )

    for defect in missing_print_measurements:

        print(
            f"Missing Print {defect['defect_id']}: "
            f"x={defect['x']}, "
            f"y={defect['y']}, "
            f"width={defect['width']}, "
            f"height={defect['height']}, "
            f"area={defect['area']}"
        )

    # =========================================================
    # MODULE 14: DEFECT ANALYSIS
    # =========================================================

    os.makedirs("results", exist_ok=True)

    # Convert detected pixel coordinates to normalized 0-1000 scale [ymin, xmin, ymax, xmax]
    formatted_defects = []
    for d in missing_print_defects:
        ymin = int((d["y"] / height) * 1000)
        xmin = int((d["x"] / width) * 1000)
        ymax = int(((d["y"] + d["height"]) / height) * 1000)
        xmax = int(((d["x"] + d["width"]) / width) * 1000)

        formatted_defects.append({
            "defect_type": "missing_print",
            "box_2d": [ymin, xmin, ymax, xmax],
            "confidence": 0.95,
            "description": f"Missing print defect detected (area: {d.get('area', 0)}px)."
        })

    detection_payload = {
        "defect_detected": len(formatted_defects) > 0,
        "defects": formatted_defects
    }

    analyzer = DefectAnalyzer()
    analysis_result = analyzer.analyze(detection_payload)
    analyzer.save_result(analysis_result, "results/defect_analysis.json")

    print("\n========================================")
    print("MODULE 14 : DEFECT ANALYSIS")
    print("========================================")
    print(f"Status: {analysis_result['inspection_status']}")
    print(f"Total Analyzed Defects: {analysis_result['total_defects']}")
    print("Saved to: results/defect_analysis.json")

    # =========================================================
    # MODULE 15: QC REPORT GENERATOR
    # =========================================================

    annotated_image_path = "results/annotated_inspection.png"
    cv2.imwrite(annotated_image_path, missing_print_result)

    report_generator = QCReportGenerator(output_directory="results")
    pdf_report_path = report_generator.generate(
        analysis_result,
        annotated_image=annotated_image_path
    )

    print("\n========================================")
    print("MODULE 15 : QC REPORT GENERATION")
    print("========================================")
    print(f"QC PDF Report generated: {pdf_report_path}")

    # =========================================================
    # 11. DISPLAY REFERENCE
    # =========================================================

    cv2.imshow(
        "Reference",
        reference
    )

    # =========================================================
    # 12. DISPLAY ORIGINAL FACTORY
    # =========================================================

    cv2.imshow(
        "Factory Original",
        factory
    )

    # =========================================================
    # 13. DISPLAY ALIGNED FACTORY
    # =========================================================

    cv2.imshow(
        "Factory Aligned",
        factory_aligned_color
    )

    # =========================================================
    # 14. MODULE 7–10 MASK
    # =========================================================

    cv2.imshow(
        "Pixel Difference Mask",
        difference_mask
    )

    # =========================================================
    # 15. MODULE 7–10 RESULT
    # =========================================================

    difference_result = draw_defect_boxes(
        factory_aligned_color,
        difference_defects
    )

    cv2.imshow(
        "Pixel Difference Defects",
        difference_result
    )

    # =========================================================
    # 16. MODULE 12 MASK
    # =========================================================

    cv2.imshow(
        "Missing Print Mask",
        missing_print_mask
    )

    # =========================================================
    # 17. MODULE 12 RESULT
    # =========================================================

    cv2.imshow(
        "Missing Print Defects",
        missing_print_result
    )

    # =========================================================
    # 18. WAIT
    # =========================================================

    print("\nPress any key in an image window to close.")

    cv2.waitKey(0)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()