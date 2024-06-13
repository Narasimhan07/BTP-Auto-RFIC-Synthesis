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
file_path_5 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/process_gain_&_s11_vs_freq/s11_ff_lib.csv"
file_path_6 = "/Users/sreyas/Documents/BTP_EE20B087/pytest/process_gain_&_s11_vs_freq/s11_ss_lib.csv"

freq_gain_tt = []
freq_gain_ss = []
freq_gain_ff = []
freq_s11_tt = []
freq_s11_ss = []
freq_s11_ff = []
gain_tt = []
gain_ss = []
gain_ff = []
s11_tt = []
s11_ss = []
s11_ff = []
freq_gain_tt, gain_tt = read_CSV(file_path_1)
freq_gain_ff, gain_ff = read_CSV(file_path_2)
freq_gain_ss, gain_ss = read_CSV(file_path_3)
freq_s11_tt, s11_tt = read_CSV(file_path_4)
freq_s11_ff, s11_ff = read_CSV(file_path_5)
freq_s11_ss, s11_ss = read_CSV(file_path_6)
fig, ax = plt.subplots()
ax.semilogx(freq_gain_tt, gain_tt, linewidth=1.0, linestyle='solid', color='blue', label="tt_lib")
ax.semilogx(freq_gain_ss, gain_ss, linewidth=1.0, linestyle='solid', color='green', label="ss_lib")
ax.semilogx(freq_gain_ff, gain_ff, linewidth=1.0, linestyle='solid', color='red', label="ff_lib")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(1e3, 10e6), ylim=(6, 8), yticks=np.linspace(5.5, 8.5, 7),
    xticks=np.array([1e3, 1e4, 1e5, 1e6, 1e7]), xlabel="Frequency (Hz)", ylabel="Gain (in dB)", 
    title="Voltage Mode Passive Mixer: Variation of Gain vs Process Corners"
    )
plt.show()
fig, ax = plt.subplots()
ax.plot(freq_s11_tt, s11_tt, linewidth=1.0, linestyle='solid', color='blue', label="tt_lib")
ax.plot(freq_s11_ss, s11_ss, linewidth=1.0, linestyle='solid', color='green', label="ss_lib")
ax.plot(freq_s11_ff, s11_ff, linewidth=1.0, linestyle='solid', color='red', label="ff_lib")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(540e6, 560e6), ylim=(-20,-5), yticks=np.linspace(-20, -5, 7), 
    xticks=np.linspace(540e6, 560e6, 9), xlabel="Frequency (Hz)", ylabel="$S_{11}$ (in dB)", 
    title="Voltage Mode Passive Mixer: Variation of $S_{11}$ vs Process Corners"
    )
plt.show()
