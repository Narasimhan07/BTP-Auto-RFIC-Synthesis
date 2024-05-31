import csv
import numpy as np
CSV_file_path = "/Users/sreyas/Documents/BTP_EE20B087/slope_ip3_curve.csv"
# the extracted points from csv are x-axis:input power in dbm and y-axis:slope of the 3rd harmonic plot 
x_values = []
y_values = []

# Open the CSV file
with open(CSV_file_path) as csvfile:
    # Create a CSV reader
    csv_reader = csv.reader(csvfile)
    # Skip the header row
    next(csv_reader)
    # Iterate over each row in the CSV file
    for row in csv_reader:
        # Assuming x-coordinates are in column A and y-coordinates are in column B
        x_values.append(float(row[0]))  # Convert to float
        y_values.append(float(row[1]))  # Convert to float
# print(x_values)
# Print or use x and y values as needed
# Note: the input power where the slope is closest to 3dB/dB is selected as the extrapolation point
x_values_nparray = np.array(x_values)
slope_error = np.abs(np.array(y_values)-3)
index = np.where(slope_error == np.min(slope_error))[0]
extrapolation_point = str(x_values_nparray[index][0])
print(extrapolation_point)

