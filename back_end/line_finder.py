import cv2 as cv
import numpy as np
import math
from collections import Counter


def line_length(line):
    """Compute Euclidean length of a line given as [x1,y1,x2,y2]."""
    x1, y1, x2, y2 = line[0]
    return math.hypot(x2 - x1, y2 - y1)


def line_angle(line):
    """Return angle in degrees (0-180) of a line defined by [x1,y1,x2,y2] or [[x1,y1,x2,y2]]."""
    if isinstance(line[0], (list, np.ndarray)):
        x1, y1, x2, y2 = line[0]
    else:
        x1, y1, x2, y2 = line
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return angle if angle >= 0 else angle + 180


def filter_lines_by_angle(lines, angle_ref, tolerance=5):
    """
    Keep lines that are within tolerance degrees of angle_ref or angle_ref+90.
    angle_ref and all angles are in degrees.
    """
    filtered = []
    for line in lines:
        ang = line_angle(line)
        # Compute difference to reference angle and its perpendicular.
        diff1 = min(abs(ang - angle_ref), 180 - abs(ang - angle_ref))
        diff2 = min(abs(ang - (angle_ref + 90) % 180), 180 - abs(ang - (angle_ref + 90) % 180))
        if diff1 <= tolerance or diff2 <= tolerance:
            filtered.append(line)
    return filtered


def point_line_distance(point, line_pt1, line_pt2):
    """Compute the distance from a point to a line (defined by two points)."""
    x0, y0 = point
    x1, y1 = line_pt1
    x2, y2 = line_pt2
    num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    den = math.hypot(x2 - x1, y2 - y1)
    if den == 0:
        return math.hypot(x0 - x1, y0 - y1)
    return num / den


def line_intersection(line1, line2):
    """Returns the intersection point of two lines defined by [x1,y1,x2,y2] or [[x1,y1,x2,y2]]."""
    x1, y1, x2, y2 = map(float, line1[0])
    x3, y3, x4, y4 = map(float, line2[0])

    # Scale factor (normalize coordinates)
    scale_factor = max(abs(x1), abs(y1), abs(x2), abs(y2), abs(x3), abs(y3), abs(x4), abs(y4))
    scale_factor = max(scale_factor, 1)  # Avoid division by zero

    # Scale down
    x1, y1, x2, y2 = x1 / scale_factor, y1 / scale_factor, x2 / scale_factor, y2 / scale_factor
    x3, y3, x4, y4 = x3 / scale_factor, y3 / scale_factor, x4 / scale_factor, y4 / scale_factor

    # Compute determinant
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    # Check if lines are nearly parallel
    if abs(denom) < 1e-6:
        return None  # No intersection

    # Compute intersection (in scaled space)
    intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    # Scale back up
    intersect_x *= scale_factor
    intersect_y *= scale_factor

    return int(intersect_x), int(intersect_y)


def get_four_intersections(intersections, image_shape):
    if len(intersections) < 4:
        return None

    # Filter out extreme outliers
    h, w = image_shape[:2]
    buffer_ratio = 0.1
    buffer_x = w * buffer_ratio
    buffer_y = h * buffer_ratio

    min_x = -buffer_x
    max_x = w + buffer_x
    min_y = -buffer_y
    max_y = h + buffer_y

    intersections = [
        (x, y)
        for (x, y) in intersections
        if min_x <= x <= max_x and min_y <= y <= max_y
    ]

    # Get center point from average
    cx = sum(p[0] for p in intersections)/len(intersections)
    cy = sum(p[1] for p in intersections)/len(intersections)

    quadrants = {
        "tl": [],
        "tr": [],
        "br": [],
        "bl": []
    }

    for x, y in intersections:
        if x < cx and y < cy:
            quadrants["tl"].append((x, y))
        elif x >= cx and y < cy:
            quadrants["tr"].append((x, y))
        elif x >= cx and y >= cy:
            quadrants["br"].append((x, y))
        elif x < cx and y >= cy:
            quadrants["bl"].append((x, y))

    selected_points = []
    for key in ["tl", "tr", "br", "bl"]:
        points = quadrants[key]
        if not points:
            return None
        # Pick the one closest to center
        closest = min(points, key=lambda p: (p[0] - cx)**2 + (p[1] - cy)**2)
        selected_points.append(closest)

    return selected_points  # In order: TL, TR, BR, BL


def get_intersections(lines):
    """Find intersections for each pair of lines (if they intersect within image bounds)."""
    intersections = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            pt = line_intersection(lines[i], lines[j])
            if pt is not None:
                intersections.append(pt)
    return np.array(intersections)


def fit_quadrilateral(intersections):
    """
    Attempts to fit a 4-point quadrilateral from the given intersection points.
    Handles both 4 points (normal case) and 3 points (triangle case by mirroring).
    """
    if intersections is None or len(intersections) < 4:
        print("Not enough points to form a quadrilateral.")
        return None

    # Convert intersections into (N,1,2) format and ensure float32
    intersections = np.array(intersections, dtype=np.float32).reshape(-1, 1, 2)

    if len(intersections) == 4:
        # Four points, normal case
        hull = cv.convexHull(intersections)
        epsilon = 0.02 * cv.arcLength(hull, True)
        approx = cv.approxPolyDP(hull, epsilon, True)
        return approx


def line_midpoint(l):
    x1, y1, x2, y2 = l
    return (x1 + x2) / 2, (y1 + y2) / 2


def angular_distance(a, b):
    """Returns the shortest distance between two angles (degrees, 0–180)"""
    diff = abs(a - b) % 180
    return min(diff, 180 - diff)


def average_line_midpoint(lines, length_thresh=100):
    mids = []
    for l in lines:
        x1, y1, x2, y2 = l[0]
        if math.hypot(x2 - x1, y2 - y1) < length_thresh:
            continue
        mids.append(line_midpoint((x1, y1, x2, y2)))
    if not mids:
        return None
    cx = sum(p[0] for p in mids) / len(mids)
    cy = sum(p[1] for p in mids) / len(mids)
    return cx, cy


def select_window_edges(lines, image_shape, length_thresh=100, angle_tolerance=45):
    """
    From a set of Hough lines [[x1,y1,x2,y2],...], pick exactly four:
     - One in each region (top, right, bottom, left) relative to the window center.
     - Only consider lines within `angle_tolerance` degrees of the expected orientation.
    """
    h, w = image_shape[:2]

    # 1) Estimate the window center by averaging midpoints of long lines
    cx, cy = average_line_midpoint(lines, length_thresh)

    # 2) Split lines into four regions
    regions = {"top": [], "right": [], "bottom": [], "left": []}
    for l in lines:
        x1,y1,x2,y2 = l[0]
        mp = line_midpoint((x1,y1,x2,y2))
        ang = line_angle((x1,y1,x2,y2))

        if y1 < cy and y2 < cy:
            regions["top"].append((l[0], ang, mp))
        if x1 > cx and x2 > cx:
            regions["right"].append((l[0], ang, mp))
        if y1 > cy and y2 > cy:
            regions["bottom"].append((l[0], ang, mp))
        if x1 < cx and x2 < cx:
            regions["left"].append((l[0], ang, mp))

    selected = {}
    for region, items in regions.items():
        if not items:
            return None

        # Determine expected angle for this region
        expected = 0 if region in ("top", "bottom") else 90

        # Filter to only those within angle_tolerance of expected
        items = [itm for itm in items if angular_distance(itm[1], expected) <= angle_tolerance]

        if not items:
            return None

        # Compute mode angle (integer binning)
        angles = [int(round(a)) for (_, a, _) in items]
        mode_angle = Counter(angles).most_common(1)[0][0]

        # Candidates matching mode_angle (±1°)
        candidates = [(l, mp) for (l, a, mp) in items
                      if abs(int(round(a)) - mode_angle) <= 1]
        if not candidates:
            return None

        # Pick the one farthest from center along region axis
        if region in ("top", "bottom"):
            best = max(candidates, key=lambda t: abs(t[1][1] - cy))
        else:
            best = max(candidates, key=lambda t: abs(t[1][0] - cx))

        selected[region] = best[0]

    # Return four lines in [top, right, bottom, left] order, each shaped (1,4)
    lines = [np.array([selected[r]], dtype=np.int32) for r in ("top", "right", "bottom", "left")]
    return (cx, cy), lines


# -------------------------
# Main processing pipeline:
# Assume combined_image is your binary edge image from DoG/Canny combination.
def process_lines(combined_image, show_output=False):
    # Detect lines using HoughLinesP
    lines = cv.HoughLinesP(
        image=combined_image,
        rho=1,
        theta=np.pi / 180,
        threshold=10,
        minLineLength=750,
        maxLineGap=55
    )
    if lines is None:
        print("No lines detected")
        return None, None

    # Find the longest line to determine the reference angle.
    longest_line = max(lines, key=line_length)
    ref_angle = line_angle(longest_line)

    # Filter lines: keep lines that are within the tolerance value of ref_angle or ref_angle+90
    filtered_lines = filter_lines_by_angle(lines, ref_angle, tolerance=12)
    if show_output is True:
        show_lines(filtered_lines, combined_image)

    # Find edge lines in each half of the image
    result = select_window_edges(filtered_lines, combined_image.shape, length_thresh=max(combined_image.shape)/4)
    if result is not None:
        midpoint, merged_lines = result
    else:
        merged_lines = filtered_lines
        midpoint = average_line_midpoint(filtered_lines)

    if show_output is True:
        show_lines(merged_lines, combined_image, intersections=[midpoint])

    # Draw merged lines into an image for visualization (optional)
    lines_img = np.zeros_like(combined_image, dtype=np.uint8)
    for line in merged_lines:
        x1, y1, x2, y2 = line[0]
        cv.line(lines_img, (x1, y1), (x2, y2), 255, 1)

    # Find intersection points from merged lines
    intersections = get_intersections(merged_lines)
    if show_output is True:
        show_lines(None, combined_image, intersections=intersections)

    # Reduce to four intersections to find quad
    reduced_intersections = get_four_intersections(intersections, combined_image.shape)

    # Fit a quadrilateral using the intersection points
    quad = fit_quadrilateral(reduced_intersections)
    if show_output is True:
        show_lines(None, combined_image, quad=quad)

    return quad, lines_img


def show_lines(lines, image, intersections=None, quad=None):
    """Displays lines, points, and/or a quad on the given image in a new window."""
    # Make a copy of the input so we don't modify the original
    if len(image.shape) == 2:
        # Grayscale → BGR
        preview = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    else:
        preview = image.copy()

    # Draw lines (in green)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv.line(preview, (x1, y1), (x2, y2), (0, 255, 0), 15)

    # Draw intersection points (as red circles)
    if intersections is not None:
        for pt in intersections:
            x, y = int(pt[0]), int(pt[1])
            cv.circle(preview, (x, y), 30, (0, 0, 255), -1)

    # Draw the fitted quadrilateral (in blue)
    if quad is not None:
        quad = np.array(quad, dtype=np.int32).reshape(-1, 1, 2)
        cv.polylines(preview, [quad], isClosed=True, color=(255, 0, 0), thickness=15)

    # --- Resize for consistent display height ---
    target_height = 700
    h, w = preview.shape[:2]
    scale = target_height / h
    new_w = int(w * scale)
    preview_resized = cv.resize(preview, (new_w, target_height), interpolation=cv.INTER_AREA)

    # Build a window title based on what's drawn
    title_parts = []
    if lines is not None:        title_parts.append("Lines")
    if intersections is not None: title_parts.append("Intersections")
    if quad is not None:         title_parts.append("Quad")
    window_name = " + ".join(title_parts) or "Preview"

    cv.imshow(window_name, preview_resized)
    cv.waitKey(0)
    cv.destroyAllWindows()