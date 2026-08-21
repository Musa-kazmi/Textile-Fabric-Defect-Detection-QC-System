# import cv2


# def resize_images(reference_image, factory_image):
#     """
#     Resize the factory image to match the reference image size.
#     """

#     height, width = reference_image.shape[:2]

#     factory_resized = cv2.resize(
#         factory_image,
#         (width, height)
#     )

#     return reference_image, factory_resized


# def convert_to_grayscale(reference_image, factory_image):
#     """
#     Convert both images from BGR to grayscale.
#     """

#     reference_gray = cv2.cvtColor(
#         reference_image,
#         cv2.COLOR_BGR2GRAY
#     )

#     factory_gray = cv2.cvtColor(
#         factory_image,
#         cv2.COLOR_BGR2GRAY
#     )

#     return reference_gray, factory_gray


# def preprocess_images(reference_image, factory_image):
#     """
#     Complete preprocessing pipeline.
#     """

#     reference_image, factory_image = resize_images(
#         reference_image,
#         factory_image
#     )

#     reference_gray, factory_gray = convert_to_grayscale(
#         reference_image,
#         factory_image
#     )

#     return reference_gray, factory_gray







import cv2


def resize_images(reference_image, factory_image):
    """
    Resize the factory image to match the reference image size.
    """

    height, width = reference_image.shape[:2]

    factory_resized = cv2.resize(
        factory_image,
        (width, height)
    )

    return reference_image, factory_resized


def convert_to_grayscale(reference_image, factory_image):
    """
    Convert both images from BGR to grayscale.
    """

    reference_gray = cv2.cvtColor(
        reference_image,
        cv2.COLOR_BGR2GRAY
    )

    factory_gray = cv2.cvtColor(
        factory_image,
        cv2.COLOR_BGR2GRAY
    )

    return reference_gray, factory_gray


def preprocess_images(reference_image, factory_image):
    """
    Complete preprocessing pipeline.

    Returns grayscale versions for alignment/detection, plus the resized
    color factory image so a color-aligned version can be produced later
    for display/output (detection logic itself stays grayscale-only).
    """

    reference_image, factory_resized_color = resize_images(
        reference_image,
        factory_image
    )

    reference_gray, factory_gray = convert_to_grayscale(
        reference_image,
        factory_resized_color
    )

    return reference_gray, factory_gray, factory_resized_color
