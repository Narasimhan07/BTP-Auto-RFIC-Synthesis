import csv
import numpy as np
CSV_file_path = "/Users/sreyas/Documents/BTP_EE20B087/pytest/s11.csv"
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
        i = 0
        for i in range(0,len(row), 2):
            x_values.append(float(row[i]))
            y_values.append(float(row[i+1]))
print(x_values)
print(y_values)