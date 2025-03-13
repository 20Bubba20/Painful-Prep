# Painful-Prep
CSCI4970-Capstone Spring 2025

## About

The Painting Prep App is an app for customers of Painless Prep. The app will allow customers to take pictures of windows to detect window dimensions, which can then be used by Painless Prep to manufacture custom window covers. The `demo_tool` is a prototype for the Painting Prep App. Currently, the `demo_tool` takes a picture containing a window as input and returns the dimensions of the window in inches. This `demo_tool` proves the project feasible.

The `two_marker_detect` tool also provides dimensions of windows in pictures, but relies on two ArUco markers placed in opposing corners of the window to do so. This tool has an increased reliability compared to the `demo_tool`. 

## Usage

To use the `demo_tool`, follow the below steps if taking a new picture. If using an existing image in the project repository, skip to step 6:

1. Go to [this website](https://chev.me/arucogen/) to generate an ArUco marker, size 100mm, marker ID 0, and in the 4x4 dictionary.
2. Save the marker and print to scale.
3. Place marker somewhere near the window to be tested.
4. Take a picture of the window, make sure that the ArUco marker is fully visible.
5. Download the image file, make sure it is in an image format supported by OpenCV as shown [here](https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html#gacbaa02cffc4ec2422dfa2e24412a99e2).
6. Make sure Python and pip are installed.
7. Navigate to the root of the project directory.
8. Run the following command to install dependencies: `pip install -r requirements.txt`
9. To run the prototype, run: `python ./back-end/demo_tool.py <path/to/image>`

Adjust the run command as necessary based on current working directory and python version. Replace `<path/to/image>` with a relative path to the desired image.

Once complete, the console should print a height and width in inches. Three images should also be made in the current working directory, named:

- canny.jpg
- contours.jpg
- lines_image.jpg

To use the `two_marker_detect` tool, follow the below steps:

1. Go to [this website](https://chev.me/arucogen/) to generate two ArUco markers, choose a single, and any two marker IDs in the 4x4 dictionary.
2. Save the markers and print to scale.
3. Place one of the markers in the top left corner of the window and the other in the bottom right corner. Make sure both are flush against the frame.
4. Take a picture of the window, make sure both markers are in the picture.
5. Download the image in a supported format. See [here](https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html#gacbaa02cffc4ec2422dfa2e24412a99e) for supported formats.
6. Make sure Python and pip are installed.
7. Navigate to the `back-end` folder of the project directory.
8. To run: `python two_marker_detect.py <path/to/image> <marker size in mm>`

## Release Notes

Code Milestone 1: The current prototype correctly detects edges of windowpanes in ideal conditions and calculates window dimensions. It is currently a command line tool. 

Code Milestone 2: `two_marker_detect` demonstrates improved reliability and accuracy over the `demo_tool`. On branch `Jerron_Branch`, a mobile application is being developed to take pictures, it currently has UI components.

## Contributing

As of 2/9 - Very Rough Project Structure is outlined. 
For Local Development Tools - 
    Angular: cd front-end, then run npm install angular
    OpenCv: cd back-end, then run pip install opencv-python
