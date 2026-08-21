import cv2
import numpy as np


def align_images(reference_image, factory_image):
    """
    Align the factory image with the reference image.

    Tries, in order:
      1. ORB feature matching (fast, good when the print has distinctive texture)
      2. Pyramid ECC alignment (works on repetitive/low-texture prints and
         normalizes lighting differences before comparing)
      3. Identity fallback (no alignment) with a warning, so the pipeline
         never hard-crashes -- lets you visually inspect why alignment failed.

    Returns:
        aligned_factory, valid_mask, transform_info

    transform_info describes exactly what warp was applied, so the SAME
    transform can be re-applied to the original color image later (for
    display/output) via apply_transform_color() -- keeping detection on
    grayscale but the final visual result in full color.
    """
    try:
        return _align_orb(reference_image, factory_image)
    except ValueError as orb_error:
        print(f"[align] ORB alignment failed ({orb_error}) -- trying ECC.")

    try:
        return _align_ecc_pyramid(reference_image, factory_image)
    except ValueError as ecc_error:
        print(f"[align] ECC alignment also failed ({ecc_error}).")
        print("[align] Falling back to NO alignment. Check that reference "
              "and factory images are actually the same design, same "
              "orientation, and similar exposure/lighting -- large "
              "differences in any of those will break automatic alignment.")
        return _identity_align(factory_image)


def apply_transform_color(color_image, transform_info, output_size):
    """
    Applies the same transform that was used to align a grayscale image
    to a color image instead -- so the final display/output keeps the
    original colors rather than looking grayscale.

    output_size: (width, height) -- normally reference_image.shape[:2] reversed
    """
    width, height = output_size
    t_type = transform_info["type"]

    if t_type == "perspective":
        return cv2.warpPerspective(
            color_image, transform_info["matrix"], (width, height)
        )
    elif t_type == "affine":
        flags = cv2.INTER_LINEAR
        if transform_info.get("inverse_map"):
            flags += cv2.WARP_INVERSE_MAP
        return cv2.warpAffine(
            color_image, transform_info["matrix"], (width, height), flags=flags
        )
    else:
        # identity -- already same size/content, nothing to warp
        return color_image


def _align_orb(reference_image, factory_image):
    """
    Align using ORB feature matching + homography.
    Raises ValueError if alignment isn't reliable.
    """

    orb = cv2.ORB_create(nfeatures=2000)

    reference_keypoints, reference_descriptors = orb.detectAndCompute(
        reference_image,
        None
    )

    factory_keypoints, factory_descriptors = orb.detectAndCompute(
        factory_image,
        None
    )

    if reference_descriptors is None or factory_descriptors is None:
        raise ValueError("Could not find enough features for alignment.")

    matcher = cv2.BFMatcher(
        cv2.NORM_HAMMING,
        crossCheck=True
    )

    matches = matcher.match(
        reference_descriptors,
        factory_descriptors
    )

    if len(matches) < 4:
        raise ValueError("Not enough matches found for alignment.")

    matches = sorted(
        matches,
        key=lambda match: match.distance
    )

    good_matches = matches[:100]

    reference_points = np.float32([
        reference_keypoints[m.queryIdx].pt
        for m in good_matches
    ]).reshape(-1, 1, 2)

    factory_points = np.float32([
        factory_keypoints[m.trainIdx].pt
        for m in good_matches
    ]).reshape(-1, 1, 2)

    homography, _ = cv2.findHomography(
        factory_points,
        reference_points,
        cv2.RANSAC,
        5.0
    )

    if homography is None:
        raise ValueError("Could not calculate image alignment.")

    height, width = reference_image.shape[:2]

    aligned_factory = cv2.warpPerspective(
        factory_image,
        homography,
        (width, height)
    )

    # Mask of pixels that came from the real factory image (255) vs.
    # black padding introduced by the warp (0). Padding must be excluded
    # from defect detection, or it gets misread as a huge "missing print" area.
    valid_mask = cv2.warpPerspective(
        np.ones(factory_image.shape[:2], dtype=np.uint8) * 255,
        homography,
        (width, height)
    )

    # SANITY CHECK: on repetitive/periodic prints (like a tiled diamond
    # grid), ORB can match the wrong repeated unit to another (e.g. diamond
    # #3 matched to diamond #47) and still pass the match-count check --
    # RANSAC then fits a homography that's self-consistent but geometrically
    # wrong, warping most of the real image content out of frame. If that
    # happens, valid_mask ends up covering only a small sliver, and the
    # real defect area gets silently excluded along with the fake padding.
    # Treat low coverage as an alignment failure rather than returning it.
    coverage = np.count_nonzero(valid_mask) / valid_mask.size
    min_valid_coverage = 0.6
    if coverage < min_valid_coverage:
        raise ValueError(
            f"ORB homography only covers {coverage:.0%} of the frame "
            f"(expected >= {min_valid_coverage:.0%}) -- likely an aliased "
            "match on a repetitive pattern, not a real alignment."
        )

    transform_info = {"type": "perspective", "matrix": homography}
    return aligned_factory, valid_mask, transform_info


def _normalize_lighting(image):
    """
    CLAHE contrast normalization -- used ONLY to help alignment find a
    transform. The actual defect comparison later still uses the original,
    un-equalized images, so lighting normalization here can't hide a real
    missing-print defect.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def _align_ecc_pyramid(reference_image, factory_image,
                        warp_mode=cv2.MOTION_EUCLIDEAN, levels=4):
    """
    Coarse-to-fine ECC alignment.

    Estimates the transform on a heavily downscaled pair first (where a
    large real-world shift becomes a small pixel shift), then progressively
    refines at higher resolutions. This gives ECC a starting point close
    enough to the true answer to actually converge, instead of cold-starting
    from zero at full resolution.

    Raises ValueError if it still can't converge, even at the coarsest level.
    """

    ref_norm = _normalize_lighting(reference_image)
    fac_norm = _normalize_lighting(factory_image)

    # Build pyramids, coarsest (smallest) first
    ref_pyramid = [ref_norm]
    fac_pyramid = [fac_norm]
    for _ in range(levels - 1):
        ref_pyramid.append(cv2.pyrDown(ref_pyramid[-1]))
        fac_pyramid.append(cv2.pyrDown(fac_pyramid[-1]))
    ref_pyramid.reverse()
    fac_pyramid.reverse()

    warp_matrix = np.eye(2, 3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 5000, 1e-6)

    for level in range(levels):
        ref_f = ref_pyramid[level].astype(np.float32) / 255.0
        fac_f = fac_pyramid[level].astype(np.float32) / 255.0

        try:
            _, warp_matrix = cv2.findTransformECC(
                ref_f, fac_f, warp_matrix, warp_mode, criteria
            )
        except cv2.error as e:
            raise ValueError(
                f"did not converge at pyramid level {level} "
                f"({'coarsest' if level == 0 else 'finer'} scale): {e}"
            )

        # Scale translation component x2 before moving to the next,
        # higher-resolution level (rotation/scale terms stay the same)
        if level < levels - 1:
            warp_matrix[:, 2] *= 2

    height, width = reference_image.shape[:2]

    aligned_factory = cv2.warpAffine(
        factory_image,
        warp_matrix,
        (width, height),
        flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP
    )

    valid_mask = cv2.warpAffine(
        np.ones(factory_image.shape[:2], dtype=np.uint8) * 255,
        warp_matrix,
        (width, height),
        flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP
    )

    coverage = np.count_nonzero(valid_mask) / valid_mask.size
    min_valid_coverage = 0.6
    if coverage < min_valid_coverage:
        raise ValueError(
            f"ECC result only covers {coverage:.0%} of the frame "
            f"(expected >= {min_valid_coverage:.0%}) -- transform is "
            "implausibly large, likely converged to a bad local optimum."
        )

    transform_info = {"type": "affine", "matrix": warp_matrix, "inverse_map": True}
    return aligned_factory, valid_mask, transform_info


def _identity_align(factory_image):
    """
    No-op alignment: passes the factory image through unchanged with a
    fully valid mask. Used as a last-resort fallback so the pipeline can
    still run and you can visually inspect the raw (unaligned) diff --
    this is a diagnostic aid, not a real fix.
    """
    valid_mask = np.ones(factory_image.shape[:2], dtype=np.uint8) * 255
    transform_info = {"type": "identity", "matrix": None}
    return factory_image, valid_mask, transform_info