import pytest
import numpy as np
import csv

import demo_tool



@pytest.mark.parametrize(("filepath", "exp_width", "exp_height"), 
    [
        ("tests/test-images/img_002.JPG", 6.25, 12)
    ]
)
def test_demo_tool(filepath, exp_width, exp_height):
    """
    @brief Test the demo_tool module for window pane detection and dimension calculation.
    
    @param filepath The path to the image file being tested.
    @param exp_width The expected width of the detected window in inches.
    @param exp_height The expected height of the detected window in inches.
    
    @details
    This test verifies that:
    - The `find_windowpane` function returns a valid numpy array.
    - The returned array has exactly four corner coordinates.
    - Each coordinate is a numpy array of shape (1,2) containing integer values.
    - The `get_window_dimensions` function correctly calculates the window dimensions.
    - The calculated width and height have an error margin of less than 20% compared to the expected values.
    """
    corners_array = demo_tool.find_windowpane(filepath)

    assert isinstance(corners_array, np.ndarray), f"Expected corners_array to be list object, got {type(corners_array)}"
    assert len(corners_array == 4), f"Expected corners_array to have 4 elements, got {len(corners_array)}"

    for i, coordinate in enumerate(corners_array):
        assert isinstance(coordinate, np.ndarray), f"Expected coordinate {i} to be of type list, got {type(coordinate)}"
        assert coordinate.shape == (1, 2), f"Expected coordinate to have 2 elements, got {len(coordinate)}"

        for j, val in enumerate(coordinate[0]):
            assert isinstance(val, (np.integer, int)), f"Expected val {j} to be of type int, got {type(val)}"
    
    actual_height, actual_width = demo_tool.get_window_dimensions(filepath, corners_array)

    assert isinstance(actual_width, (int, float)), f"Expected the width to be int or float, got {type(actual_width)}"
    assert isinstance(actual_height, (int, float)), f"Expected the width to be int or float, got {type(actual_height)}"

    print(actual_height, actual_width)

    w_err = abs((actual_width - exp_width) / exp_width)
    h_err = abs((actual_height - exp_height) / exp_height)

    assert w_err < 0.2, f"Expected width percent error less than 20%, got {(w_err * 100):.0f}%"
    assert h_err < 0.2, f"Expected height percent error less than 20%, got {(w_err * 100):.0f}%"