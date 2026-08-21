import cv2


def load_images(reference_path, factory_path):
    """
    Load reference and factory images.

    Returns:
        reference_image: Correct/reference print image
        factory_image: Actual factory-produced print image
    """

    reference_image = cv2.imread(reference_path)
    factory_image = cv2.imread(factory_path)

    if reference_image is None:
        raise ValueError(f"Could not load reference image: {reference_path}")

    if factory_image is None:
        raise ValueError(f"Could not load factory image: {factory_path}")

    return reference_image, factory_image


def validate_images(reference_image, factory_image):
    """
    Check whether the two images are suitable for further processing.
    """

    reference_height, reference_width = reference_image.shape[:2]
    factory_height, factory_width = factory_image.shape[:2]

    print(f"Reference image: {reference_width} x {reference_height}")
    print(f"Factory image:   {factory_width} x {factory_height}")

    if reference_image.size == 0 or factory_image.size == 0:
        raise ValueError("One of the images is empty.")

    return True


if __name__ == "__main__":

    reference_path = r"C:\Users\User\Downloads\Textile_fabrics\opencv\refrence.png"
    factory_path = r"C:\Users\User\Downloads\Textile_fabrics\opencv\manufactured.png"

    reference, factory = load_images(
        reference_path,
        factory_path
    )

    validate_images(reference, factory)

    cv2.imshow("Reference Image", reference)
    cv2.imshow("Factory Image", factory)

    cv2.waitKey(0)
    cv2.destroyAllWindows()