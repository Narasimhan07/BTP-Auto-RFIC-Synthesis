import csv
import numpy as np
import os
import matplotlib.pyplot as plt 
# Function to read CSV file and return data in columns A and B as lists
def read_CSV(CSV_file_path):
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
        # END for loop
    return x_values, y_values
file_path_1 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/temp_s11_vs_freq/s11_temp_-40.csv"
file_path_2 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/temp_s11_vs_freq/s11_temp_0.csv"
file_path_3 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/temp_s11_vs_freq/s11_temp_40.csv"
file_path_4 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/temp_s11_vs_freq/s11_temp_80.csv"
file_path_5 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/temp_s11_vs_freq/s11_temp_120.csv"

freq_minus_40 = []
freq_0 = []
freq_40 = []
freq_80 = []
freq_120 = []
s11_minus_40 = []
s11_0 = []
s11_40 = []
s11_80 = []
s11_120 = []
freq_minus_40, s11_minus_40 = read_CSV(file_path_1)
freq_0, s11_0 = read_CSV(file_path_2)
freq_40, s11_40 = read_CSV(file_path_3)
freq_80, s11_80 = read_CSV(file_path_4)
freq_120, s11_120 = read_CSV(file_path_5)
fig, ax = plt.subplots()
ax.plot(freq_minus_40, s11_minus_40, linewidth=1.0, linestyle='solid', color='red', label="$-40^{\circ}$ C")
ax.plot(freq_0, s11_0, linewidth=1.0, linestyle='solid', color='blue', label="$0^{\circ}$ C")
ax.plot(freq_40, s11_40, linewidth=1.0, linestyle='solid', color='orange', label="$40^{\circ}$ C")
ax.plot(freq_80, s11_80, linewidth=1.0, linestyle='solid', color='green', label="$80^{\circ}$ C")
ax.plot(freq_120, s11_120, linewidth=1.0, linestyle='solid', color='purple', label="$120^{\circ}$ C")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(540e6, 560e6), ylim=(-16,-7), yticks=np.linspace(-16, -7, 10), 
    xticks=np.linspace(540e6, 560e6, 9), xlabel="Frequency (Hz)", ylabel="$S_{11}$ (in dB)", 
    title="Voltage Mode Passive Mixer: Variation of $S_{11}$ vs Temperature"
    )
plt.show()
