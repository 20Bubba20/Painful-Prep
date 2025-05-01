import os
import sys
import csv
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import demo_tool
import demo_tool_v2
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
            'width': float(row["window_width"]),
            'height': float(row["window_height"])
        }

# creating the results list to be put into the csv file later
results = []
accuracy_scores = []
one_marker_accuracies = []
two_marker_accuracies = []
one_marker_v2_accuracies = []
one_marker_attempts = 0
two_marker_attempts = 0
one_marker_v2_attempts = 0
one_marker_success = 0
two_marker_success = 0
one_marker_v2_success = 0

def run_demo_tool():
    """
    Run the one marker detection demo tool on all images with one marker and a false ignore flag in data.csv
    """

    #global variables
    global one_marker_attempts, one_marker_success, one_marker_accuracies, accuracy_scores, results

    print("Results for one marker deteciton using demo_tool: ")
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
                        ignore_flag = row["ignore"].strip().lower() == 'true'
                        break

            # run demo_tool only if there is one marker and ignore flag is false
            if marker_quantity == 1 and not ignore_flag:
                one_marker_attempts += 1
                try:
                    #find corners of the windowpane
                    corners_array = demo_tool.find_windowpane(img_path)

                    #gets width and height of the windowpane
                    raw_width, raw_height = demo_tool.get_window_dimensions(img_path, corners_array)

                    measured_width = round(raw_width, 2)
                    measured_height = round(raw_height, 2)

                    #finds the expected width and height from data.csv
                    expected_width = expected_data[img_id]['width']
                    expected_height = expected_data[img_id]['height']

                    #finds the percent error for the width and height per window
                    width_error = abs((measured_width - expected_width) / expected_width) * 100
                    height_error = abs((measured_height - expected_height) / expected_height) * 100
                    average_error = (width_error + height_error) / 2

                    #calculates accuracy score
                    accuracy_score = round(max(0.0, 1-(average_error / 100)), 2)

                    one_marker_accuracies.append(accuracy_score)
                    accuracy_scores.append(accuracy_score)
                    one_marker_success += 1

                    #calculate the difference between expected and measured values
                    diff_width = round(measured_width - expected_width, 2)
                    diff_height = round(measured_height - expected_height, 2)

                    #appends the results to the results list
                    results.append([img_id, measured_width, measured_height, expected_width, expected_height, diff_width, diff_height, accuracy_score, "demo_tool"])

                except Exception as e:
                    print(f"Error processing {img_id}: {e}")

    if one_marker_attempts:
        average_accuracy = round((sum(one_marker_accuracies) / len(one_marker_accuracies)) * 100, 2) if one_marker_accuracies else 0.0
        reliability = round((one_marker_success / one_marker_attempts) * 100, 2)
        print(f"Average accuracy for one marker detection using demo_tool: {average_accuracy}% | Reliability for one marker detection using demo_tool: {reliability}%\n")
    else:
        print("No one marker images processed.")


def run_two_marker_detect():
    """
    Run the two marker detection on all images with two markers and a false ignore flag in data.csv
    This function also separates which marker type is used in the image.
    """
    print("Results for two marker detection using two_marker_detect: ")

    #global variables
    global two_marker_attempts, two_marker_success, two_marker_accuracies, accuracy_scores, results

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
                        ignore_flag = row["ignore"].strip().lower() == 'true'
                        break

            # run demo_tool only if there is one marker and ignore flag is false
            if marker_quantity == 2 and not ignore_flag:
                two_marker_attempts += 1
                try:
                    #get the marker size from data.csv
                    with open(data_csv, newline='') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if img_id == row["id"]:
                                marker_size = int(row["marker_size"])
                                marker_type = row["marker_type"]
                                break

                    #calculate the width and height of the windowpane
                    raw_width, raw_height = two_marker_detect.calculate_two_markers(img_path, marker_size, marker_type)

                    measured_width = round(raw_width, 2)
                    measured_height = round(raw_height, 2)

                    #checks if the actual width and height are None if the image is not detected
                    if measured_width is None or measured_height is None:
                        print(f"Error: Unable to calculate dimensions for {img_id}")
                        continue

                    #find expected width and height from data.csv
                    expected_width = expected_data[img_id]['width']
                    expected_height = expected_data[img_id]['height']

                    #find the percent error for the width and height per window
                    width_error = abs((measured_width - expected_width) / expected_width) * 100
                    height_error = abs((measured_height - expected_height) / expected_height) * 100
                    average_error = (width_error + height_error) / 2

                    #generate accuracy of the window detection
                    accuracy = round(max(0.0, 1 - (average_error / 100)), 2)

                    two_marker_accuracies.append(accuracy)
                    accuracy_scores.append(accuracy)
                    two_marker_success += 1

                    #calculate the difference between expected and measured values
                    diff_width = round(measured_width - expected_width, 2)
                    diff_height = round(measured_height - expected_height, 2)

                    results.append([img_id, measured_width, measured_height, expected_width, expected_height, diff_width, diff_height, accuracy, "two_marker"])

                except Exception as e:
                    print(f"Error processing {img_id}: {e}")

    if two_marker_attempts:
        average_accuracy = round(sum(two_marker_accuracies) / len(two_marker_accuracies) * 100, 2) if two_marker_accuracies else 0.0
        reliability = round((two_marker_success / two_marker_attempts) * 100, 2)
        print(f"Average accuracy for two marker detection: {average_accuracy}% | Reliability for two marker detection: {reliability}%\n")
    else:
        print("No two marker images processed.")

def run_demo_tool_v2():
    """
    Run the one marker detection v2 on all images with one marker and a false ignore flag in data.csv
    """
    print("Results for one marker detection using demo_tool_v2:")

    #global variables
    global one_marker_v2_attempts, one_marker_v2_success, one_marker_v2_accuracies, accuracy_scores, results

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
                        ignore_flag = row["ignore"].strip().lower() == 'true'
                        break

            # run demo_tool only if there is one marker and ignore flag is false
            if marker_quantity == 1 and not ignore_flag:
                one_marker_v2_attempts += 1
                try:
                    #find corners of the windowpane
                    corners_array = demo_tool_v2.find_windowpane(img_path)

                    #gets width and height of the windowpane
                    raw_width, raw_height = demo_tool_v2.get_window_dimensions(img_path, corners_array)

                    measured_width = round(raw_width, 2)
                    measured_height = round(raw_height, 2)

                    #finds the expected width and height from data.csv
                    expected_width = expected_data[img_id]['width']
                    expected_height = expected_data[img_id]['height']

                    #finds the percent error for the width and height per window
                    width_error = abs((measured_width - expected_width) / expected_width) * 100
                    height_error = abs((measured_height - expected_height) / expected_height) * 100
                    average_error = (width_error + height_error) / 2

                    #calculates accuracy score
                    accuracy_score = round(max(0.0, 1-(average_error / 100)), 2)

                    one_marker_v2_accuracies.append(accuracy_score)
                    accuracy_scores.append(accuracy_score)
                    one_marker_v2_success += 1
                    
                    #calculate the difference between expected and measured values
                    diff_width = round(measured_width - expected_width, 2)
                    diff_height = round(measured_height - expected_height, 2)

                    #appends the results to the results list
                    results.append([img_id, measured_width, measured_height, expected_width, expected_height, diff_width, diff_height, accuracy_score, "demo_tool_v2"])

                except Exception as e:
                    print(f"Error processing {img_id}: {e}")

    if one_marker_attempts:
        average_accuracy = round((sum(one_marker_v2_accuracies) / len(one_marker_v2_accuracies)) * 100, 2) if one_marker_v2_accuracies else 0.0
        reliability = round((one_marker_v2_success / one_marker_v2_attempts) * 100, 2)
        print(f"Average accuracy for one marker detection using demo_tool: {average_accuracy}% | Reliability for demo_tool_v2: {reliability}%\n")
    else:
        print("No one marker images processed.")

def report_best_and_worst_results(results):
    """
    Report the best case (image with the smallest absolute sum of diff_width and diff_height)
    and the worst case (image with the largest absolute sum of diff_width and diff_height) 
    """
    if not results:
        print("No results to report.")
        return
    
    def total_diff(result):
        return abs(result[5]) + abs(result[6])
    
    best_case = min(results, key=total_diff)
    worst_case = max(results, key=total_diff)

    print("\nBest Case (lowest total difference):")
    print(f"  ID: {best_case[0]} | Method: {best_case[8]}")
    print(f"  Measured: {best_case[1]} x {best_case[2]} | Expected: {best_case[3]} x {best_case[4]}")
    print(f"  Diffs => Height: {best_case[5]}, Width: {best_case[6]} | Accuracy: {best_case[7]*100:.2f}%")

    print("\nWorst Case (highest total difference):")
    print(f"  ID: {worst_case[0]} | Method: {worst_case[8]}")
    print(f"  Measured: {worst_case[1]} x {worst_case[2]} | Expected: {worst_case[3]} x {worst_case[4]}")
    print(f"  Diffs => Height: {worst_case[5]}, Width: {worst_case[6]} | Accuracy: {worst_case[7]*100:.2f}%")


def save_results(filename, data):
    """
    Save the results to a CSV file
    """
    header = [
        "id", 
        "measured_width",
        "measured_height",
        "expected_width",
        "expected_height",
        "diff_width",
        "diff_height",
        "accuracy_score",
        "method"
    ]
    with open(filename, mode="w", newline="" ) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


if __name__ == "__main__":
    run_demo_tool()
    run_two_marker_detect()
    run_demo_tool_v2()
    report_best_and_worst_results(results)
    save_results("test-images/results.csv", results)
