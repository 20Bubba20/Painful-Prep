import cv2 as cv
import numpy as np
import math


def line_length(line):
    """Compute Euclidean length of a line given as [x1,y1,x2,y2]."""
    x1, y1, x2, y2 = line[0]
    return math.hypot(x2 - x1, y2 - y1)


def line_angle(line):
    """Return angle in degrees (0-180) of a line defined by [x1,y1,x2,y2]."""
    x1, y1, x2, y2 = line[0]
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    # Normalize to 0-180 range
    if angle < 0:
        angle += 180
    return angle


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


def merge_lines(lines, distance_thresh=20, angle_thresh=5):
    """
    Merge lines that are close and collinear.
    This is a simple heuristic approach.
    Each line is represented as [x1,y1,x2,y2].
    """
    merged = []
    used = [False] * len(lines)

    for i, line1 in enumerate(lines):
        if used[i]:
            continue
        x1, y1, x2, y2 = line1[0]
        pts = [(x1, y1), (x2, y2)]
        used[i] = True
        for j in range(i + 1, len(lines)):
            if used[j]:
                continue
            # Compare line1 with line2
            x3, y3, x4, y4 = lines[j][0]
            ang1 = line_angle(line1)
            ang2 = line_angle(lines[j])
            if abs(ang1 - ang2) > angle_thresh:
                continue
            # Check if endpoints are close (using point-to-line distance)
            dist1 = point_line_distance((x3, y3), (x1, y1), (x2, y2))
            dist2 = point_line_distance((x4, y4), (x1, y1), (x2, y2))
            if dist1 < distance_thresh and dist2 < distance_thresh:
                pts.extend([(x3, y3), (x4, y4)])
                used[j] = True
        # Merge all points by taking the extreme ones along the main orientation
        pts = np.array(pts)
        # Project points on the line direction vector:
        theta = np.deg2rad(ang1)
        proj = pts[:, 0] * math.cos(theta) + pts[:, 1] * math.sin(theta)
        min_idx = np.argmin(proj)
        max_idx = np.argmax(proj)
        merged_line = np.array([pts[min_idx][0], pts[min_idx][1], pts[max_idx][0], pts[max_idx][1]])
        merged.append(np.array([merged_line]))
    return merged


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

    height, width = image_shape[:2]
    cx, cy = width // 2, height // 2

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
    Uses convex hull and polygon approximation.
    """
    # Ensure shape is correct for OpenCV functions
    intersections = np.array(intersections, dtype=np.float32).reshape(-1, 1, 2)

    # Compute convex hull
    hull = cv.convexHull(intersections)

    # Approximate polygon from hull
    epsilon = 0.02 * cv.arcLength(hull, True)
    approx = cv.approxPolyDP(hull, epsilon, True)

    # print("Quadrilateral found:", approx.reshape(-1, 2))
    return approx  # Still in (N, 1, 2) format, as expected by OpenCV drawing funcs


def merge_similar_lines(lines, angle_threshold=np.deg2rad(2), dist_threshold=20):
    if lines is None or len(lines) == 0:
        return []

    lines = np.array(lines).reshape(-1, 4)
    merged = []

    for i in range(len(lines)):
        x1, y1, x2, y2 = lines[i]
        angle_i = np.arctan2((y2 - y1), (x2 - x1))

        keep = True
        for j in range(len(merged)):
            mx1, my1, mx2, my2 = merged[j]
            angle_j = np.arctan2((my2 - my1), (mx2 - mx1))

            if abs(angle_i - angle_j) < angle_threshold:
                keep = False
                break

        if keep:
            merged.append([x1, y1, x2, y2])

    # Convert to Format A
    return [np.array([[x1, y1, x2, y2]], dtype=np.int32) for x1, y1, x2, y2 in merged]


# -------------------------
# Main processing pipeline:
# Assume combined_image is your binary edge image from DoG/Canny combination.
def process_lines(combined_image, show_output=False):
    # Detect lines using HoughLinesP
    lines = cv.HoughLinesP(
        image=combined_image,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=1000,
        maxLineGap=70
    )
    if lines is None:
        print("No lines detected")
        return None, None

    # Find the longest line to determine the reference angle.
    longest_line = max(lines, key=line_length)
    ref_angle = line_angle(longest_line)

    # Filter lines: keep lines that are within 5 degrees of ref_angle or ref_angle+90
    filtered_lines = filter_lines_by_angle(lines, ref_angle, tolerance=9)
    if show_output is True:
        show_lines(filtered_lines, combined_image)

    # (Optional) Further filtering by length if needed (already set in HoughLinesP)

    # Merge close and collinear lines
    # merged_lines = merge_lines(filtered_lines, distance_thresh=20, angle_thresh=7)
    # merged_lines = merge_similar_lines(np.array(merged_lines))
    merged_lines = merge_similar_lines(filtered_lines)

    if show_output is True:
        show_lines(merged_lines, combined_image)

    # Draw merged lines into an image for visualization (optional)
    lines_img = np.zeros_like(combined_image, dtype=np.uint8)
    for line in merged_lines:
        x1, y1, x2, y2 = line[0]
        cv.line(lines_img, (x1, y1), (x2, y2), 255, 1)

    # Find intersection points from merged lines
    intersections = get_intersections(merged_lines)
    if show_output is True:
        show_lines(None, combined_image, intersections=intersections)

    # Redyuce to four intersections to find quad
    reduced_intersections = get_four_intersections(intersections, combined_image.shape)

    # Fit a quadrilateral using the intersection points
    quad = fit_quadrilateral(reduced_intersections)
    if show_output is True:
        show_lines(None, combined_image, quad=quad)

    return quad, lines_img


def show_lines(lines, image, intersections=None, quad=None):
    # Prepare a blank canvas for drawing
    if len(image.shape) == 2:
        preview = cv.cvtColor(np.zeros_like(image), cv.COLOR_GRAY2BGR)
    else:
        preview = np.zeros_like(image)

    # Draw lines (in green)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv.line(preview, (x1, y1), (x2, y2), (0, 255, 0), 3)

    # Draw intersection points (as red circles)
    if intersections is not None:
        for pt in intersections:
            x, y = int(pt[0]), int(pt[1])
            cv.circle(preview, (x, y), 10, (0, 0, 255), -1)

    # Draw the fitted quadrilateral (in blue)
    if quad is not None:
        quad = np.array(quad, dtype=np.int32).reshape((-1, 1, 2))
        cv.polylines(preview, [quad], isClosed=True, color=(255, 0, 0), thickness=2)

    # --- Resize for consistent display height ---
    target_height = 700
    original_height, original_width = preview.shape[:2]
    scale_factor = target_height / original_height
    new_width = int(original_width * scale_factor)

    preview_resized = cv.resize(preview, (new_width, target_height), interpolation=cv.INTER_AREA)

    window_name = ""
    if lines is not None:
        window_name += " Lines "
    if quad is not None:
        window_name += " Quad "
    if intersections is not None:
        window_name += " Intersections "
    # Show the image
    cv.imshow(window_name, preview_resized)
    cv.waitKey(0)
    cv.destroyAllWindows()