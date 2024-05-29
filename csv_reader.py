import csv
import numpy as np
import os

run_spectre_command = "spectre VM_iip3.scs +escchars +log ./psf/spectre.out -format psfxl -raw ./psf ++aps +lqtimeout 900 -maxw 5 -maxn 5"
os.system(run_spectre_command)
os.system("ocean -restore write_ip3_slope_to_CSV.ocn")
# Replace 'your_file.csv' with the actual path to your CSV file
file_path = "slope_ip3_curve.csv"

x_values = []
y_values = []

# Open the CSV file
with open(file_path) as csvfile:
    	# Create a CSV reader
    	csv_reader = csv.reader(csvfile)
    	# Skip the header row
    	next(csv_reader)
    	# Iterate over each row in the CSV file
    	for row in csv_reader:
		# Assuming x-coordinates are in column A and y-coordinates are in column B
		x_values.append(float(row[0]))  # Convert to float if necessary
		y_values.append(float(row[1]))  # Convert to float if necessary

# Print or use x and y values as needed
#print("X coordinates:", x_values)
#print("Y coordinates:", y_values)
pin = np.array(x_values)
slope_error = np.abs(np.array(y_values)-3)
index = np.where(slope_error == np.min(slope_error))[0]
extrapolation_point = str(x_values[index])

ocn_file_path = "extract_iip3_post_optimization.ocn"
with open(ocn_file_path, 'r') as file:
	ocn_content = file.readlines()
	# print(scs_content)
	new_line = ""
	ocn_new_content = list()
        for line in ocn_content:
        	line = line.strip()
            	words = line.split(' ')
            	if(words[0] == "iip3"):
			words[7] = extrapolation_point
                new_line = ' '.join(words)
                # print(new_line)
                ocn_new_content.append(new_line + " \n")

with open(ocn_file_path, 'w') as file:
	file.writelines(ocn_new_content)

os.system("ocean -restore extract_iip3_post_optimization.ocn")





	
	

