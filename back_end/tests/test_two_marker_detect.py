'To run tests, go to back_end/tests directory, and run pytest from there.'

import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import two_marker_detect

@pytest.mark.parametrize(
        "marker_corners, expected",
        [
            (np.array([[0, 0], [0, 100], [100, 100], [100, 0]]), 100),
            (np.array([[0, 100], [100, 100], [100, 0], [0, 0]]), 100),
            (np.array([[100, 100], [100, 0], [0, 0], [0, 100]]), 100),
            (np.array([[100, 0], [0, 0], [0, 100], [100, 100]]), 100),
            (np.array([[0, 0], [0, 100], [50, 100], [50, 0]]), 75)
        ]
)
def test_get_scale(marker_corners, expected):
    assert two_marker_detect.get_scale(marker_corners) == expected

@pytest.mark.parametrize(
        "corner_coords, orientation, expected",
        [
            (np.array([[0, 0], [1, 101], [100, 100], [101, 1]]), "TLBR", (0, 0, 100, 100)),
            (np.array([[0, 0], [1, 101], [100, 100], [101, 1]]), "TRBL", (101, 1, 1, 101)),
            (np.array([[101, 1], [0, 0], [1, 101], [100, 100]]), "TLBR", (0, 0, 100, 100)),
            (np.array(
                [[0, 0], [1, 101], [100, 100], [101, 1],
                 [200, 200], [201, 301], [300, 300], [301, 200]]), "TLBR", (0, 0, 300, 300)),
            (np.array(
                [[1, 200], [0, 300], [100, 200], [101, 300],
                 [300, 0], [200, 0], [201, 100], [301, 100]]), "TRBL", (300, 0, 0, 300))
        ]
)
def test_get_diff_two_markers_px(corner_coords, orientation, expected):
    assert two_marker_detect.get_diff_two_markers_px(corner_coords, orientation) == expected
