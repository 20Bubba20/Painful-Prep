import os
import sys
import csv
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import demo_tool
import two_marker_detect

# paths to the images folder, data.csv and results.csv
test_images = "test-images"
data_csv = "test-images/data.csv"
results_csv = "test-images/results.csv"

# finding the expected width and height from data.csv
expected_data = {}
with open(data_csv, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        expected_data[row["id"]] = {
            'width': round(float(row["window_width"])),
            'height': round(float(row["window_height"]))
        }

# creating the results list to be put into the csv file later
results = []

# making sure that the img_id exists, matches the file name, and is the right file type 
for filename in os.listdir(test_images):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(test_images, filename)
        img_id = filename

        # error if the file name does not match the id in data.csv
        if img_id not in expected_data:
            print(f"Warning: {img_id} not found in data.csv")
            continue

        # gets the marker quantity per img_id
        with open(data_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if img_id == row["id"]:
                    marker_quantity = int(row["marker_quantity"])
                    break
            
        """
        Try-Catch block for each detection method that is being tested

        If the marker_quantity for the given img_id = 1, then demo_tool is used
            Args: path, corners_array (for get_window_dimensions)
            Returns: tuple of (actual_width, actual_height)
        
        If the marker_quantity for the given img_id = 2, then two_marker_detect is used
            Args: path, marker_size
            Returns: tuple of (actual_width, actual_height)

        Both implementations append the results of their runs to the results list
        """
        try:
            # check if marker_quantity = 1
            if marker_quantity == 1:
                #find corners_array
                corners_array = demo_tool.find_windowpane(img_path)

                #gets height and width form demo_tool calculation
                raw_height, raw_width = demo_tool.get_window_dimensions(img_path, corners_array)

                actual_height = round(raw_height, 2)
                actual_width = round(raw_width, 2)

                # finds the expected width and height from data.csv
                expected_width = expected_data[img_id]['width']
                expected_height = expected_data[img_id]['height']

                # finds the percent error for the width and height per window
                w_err = abs((actual_width - expected_width) / expected_width)
                h_err = abs((actual_height - expected_height) / expected_height)
                avg_error = (w_err + h_err) / 2

                #generates the accuracy of the window detection
                accuracy = round(1 - avg_error, 2)

                # appends results to the list
                results.append([img_id, actual_width, actual_height, expected_width, expected_height, accuracy])

            # check if marker_quantity = 2
            elif marker_quantity == 2:
                # gets the marker size from data.csv
                with open(data_csv, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if img_id == row["id"]:
                            marker_size = int(row["marker_size"])
                            break

                # calculates the actual height and width using two_marker_detect
                raw_height, raw_width = two_marker_detect.calculate_two_markers(img_path, marker_size)

                actual_height = round(raw_height, 2)
                actual_width = round(raw_width, 2)

                # checks if the actual height and width are None (if the image is not detected)
                if actual_height is None or actual_width is None:
                    print(f"Error: Unable to calculate dimensions for {img_id}")
                    continue

                # finds the expected width and height from data.csv
                expected_height = expected_data[img_id]['height']
                expected_width = expected_data[img_id]['width']

                # finds the percent error for the width and height per window
                w_err = abs((actual_width - expected_width) / expected_width)
                h_err = abs((actual_height - expected_height) / expected_height)
                avg_error = (w_err + h_err) / 2

                #generates the accuracy of the window detection
                accuracy = round(1 - avg_error, 2)

                # appends results to the list
                results.append([img_id, actual_width, actual_height, expected_width, expected_height, accuracy])
            
            # error check for invalid marker quantities
            else:
                raise ValueError(f"Invalid marker quantity: {marker_quantity}")

        # if the image is not detected, or if there is an error in the detection process
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# creates results.csv with the data from the results list
with open(results_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "actual_width", "actual_height", "expected_width", "expected_height", "accuracy"])
    writer.writerows(results)

# print to confirm that results.csv was created successfully
print(f"Results saved to {results_csv}")