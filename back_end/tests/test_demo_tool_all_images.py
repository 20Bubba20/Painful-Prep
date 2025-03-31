"""
Gamplan for this file:
- Run all test images through the demo_tool script
- Compare the calculated dimensions with the expected dimensions
- calculate the average percent error for width and height of all windows
- if the error is within 20% of the expected value, the test passes
- save the following results into a new csv file
- RUN FROM TESTS DIRECTORY
"""

import os
import sys
import csv
import datetime
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import demo_tool

test_images = "test-images"
data_csv = "test-images/data.csv"
results_csv = "test-images/results.csv"

expected_data = {}
with open(data_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        expected_data[row["id"]] = {
            'width': float(row["window_width"]),
            'height': float(row["window_height"])
        }

results = []

for filename in os.listdir(test_images):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(test_images, filename)
        img_id = filename

        if img_id not in expected_data:
            print(f"Warning: {img_id} not found in data.csv")
            continue

        try:
            corners_array = demo_tool.find_windowpane(img_path)
            actual_height, actual_width = demo_tool.get_window_dimensions(img_path, corners_array)

            expected_width = expected_data[img_id]['width']
            expected_height = expected_data[img_id]['height']

            w_err = abs((actual_width - expected_width) / expected_width)
            h_err = abs((actual_height - expected_height) / expected_height)
            avg_error = (w_err + h_err) / 2
            accuracy = 1 - avg_error

            results.append([img_id, actual_width, actual_height, expected_width, expected_height, accuracy])

        except Exception as e:
            print(f"Error processing {filename}: {e}")

with open(results_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "actual_width", "actual_height", "expected_width", "expected_height", "accuracy"])
    writer.writerows(results)

print(f"Results saved to {results_csv}")