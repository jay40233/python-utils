import cv2
import numpy as np
import math

def detect_arrow_tip_and_angle(image_path):
    """
    Detects the tip of the arrow in the image and calculates its angle against the horizontal axis.
    Returns (tip_x, tip_y, angle_degrees)
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Convert to grayscale and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Assume the largest contour is the arrow
    arrow_contour = max(contours, key=cv2.contourArea)

    # Find the farthest point from the contour's centroid (likely the tip)
    M = cv2.moments(arrow_contour)
    if M["m00"] == 0:
        raise ValueError("Contour area is zero.")
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    tip = max(arrow_contour, key=lambda pt: np.linalg.norm(np.array([cx, cy]) - pt[0]))
    tip_x, tip_y = tip[0]

    # Calculate angle against horizontal
    dx = tip_x - cx
    dy = tip_y - cy
    angle_rad = math.atan2(-dy, dx)  # Negative dy because image y-axis is downward
    angle_deg = math.degrees(angle_rad)

    return (tip_x, tip_y, angle_deg)

# Example usage:
if __name__ == "__main__":
    tip_x, tip_y, angle = detect_arrow_tip_and_angle("wind_example.jpg")
    print(f"Arrow tip at ({tip_x}, {tip_y}), angle: {angle:.2f} degrees")