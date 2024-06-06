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
file_path_1 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/process_gain_&_s11_vs_freq/gain_tt_lib.csv"
file_path_2 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/process_gain_&_s11_vs_freq/gain_ff_lib.csv"
file_path_3 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/process_gain_&_s11_vs_freq/gain_ss_lib.csv"
file_path_4 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/process_gain_&_s11_vs_freq/s11_tt_lib.csv"
file_path_5 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/process_gain_&_s11_vs_freq/gain_tt_lib.csv"
file_path_6 = ""

freq_minus_40 = []
freq_0 = []
freq_40 = []
freq_80 = []
freq_120 = []
gain_minus_40 = []
gain_0 = []
gain_40 = []
gain_80 = []
gain_120 = []
freq_minus_40, gain_minus_40 = read_CSV(file_path_1)
freq_0, gain_0 = read_CSV(file_path_2)
freq_40, gain_40 = read_CSV(file_path_3)
freq_80, gain_80 = read_CSV(file_path_4)
freq_120, gain_120 = read_CSV(file_path_5)
fig, ax = plt.subplots()
ax.semilogx(freq_minus_40, gain_minus_40, linewidth=1.0, linestyle='solid', color='red', label="$-40^{\circ}$ C")
ax.semilogx(freq_0, gain_0, linewidth=1.0, linestyle='solid', color='blue', label="$0^{\circ}$ C")
ax.semilogx(freq_40, gain_40, linewidth=1.0, linestyle='solid', color='orange', label="$40^{\circ}$ C")
ax.semilogx(freq_80, gain_80, linewidth=1.0, linestyle='solid', color='green', label="$80^{\circ}$ C")
ax.semilogx(freq_120, gain_120, linewidth=1.0, linestyle='solid', color='magenta', label="$120^{\circ}$ C")
ax.grid()
ax.legend(loc=1)
ax.set(xlim=(1e3, 10e6), ylim=(5.5,7.5), 
    xticks=np.array([1e3, 1e4, 1e5, 1e6, 1e7]), xlabel="Frequency (Hz)", ylabel="Gain (in dB)", 
    title="VM Passive Mixer: Variation of Gain vs Temperature"
    )
plt.show()
