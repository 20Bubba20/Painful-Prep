"""
Gamplan for this file:
- Run all test images through the demo_tool script
- Compare the calculated dimensions with the expected dimensions
- calculate the average percent error for width and height of all windows
- if the error is within 20% of the expected value, the test passes
- save the results in a sqlite database storing timestamp, image_id, calculated_width, calculated_height, expected_width, expected_height, accuracy_score (composite key of timestamp and accuracy_score)
"""