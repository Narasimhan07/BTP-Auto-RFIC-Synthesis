# =========================================== COMMON FUNCTIONS REPOSITORY ================================================================
# This file contains the required function definitions to carry out file reading, mathematical computations etc.
#import numpy as np
import os
import copy
import csv
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------- RAMP FUNCTION for LOSS ---------------------------------------------------
def ramp_func(x):
	if x>0:
		return x
	else:
		return 0
# ---------- END of RAMP function --------------------------
# ----------------------------------------------- SQR FUNCTION for LOSS ----------------------------------------------------
def sqr_func(x):
    return pow(x,2)
# ---------- END of SQR function ---------------------------
# -------------------------------------- FUNCTION to ROUND-OFF to NEAREST INTEGER ------------------------------------------
def round_off_fun(x):
    if x>0:
        y = x - int(x)
        if y>=0.5:
            return float(int(x) + 1)
        else:
            return float(int(x))
    else:
        y = x - int(x)
        if y<=-0.5:
            return float(int(x) - 1)
        else:
            return float(int(x))
# -------- END of round_off_fun() --------------------------
"""
===========================================================================================================================
----------------------------------------- FUNCTIONS TO EDIT TSMC 65NM COMPONENTS ------------------------------------------
"""
# below function sets the value of resistance width for TSMC 65nm PDK component "rppoly_rf"
def set_rppoly_rf_w(RB, res_count):
    # based on the number of resistors in series we define RB_per_res
    RB_per_res = RB/float(res_count)
    # for w = 10u and l = 2u, resistance = 78.1792
    RB_ref = 78.1792
    res_w = 10*(RB_per_res/RB_ref)
    # width of the resistance is res_w*1u
    # note that if res_w fall below the required min width, then default width has to be be set
    # Note: this calculation is an approximation and is off by some 10 ohms from RB value required
    return res_w
# END of set_rppoly_rf_w()

# below function sets the value of length and width of the capacitance element "mimcap_um_rf"
# the RC tank contains "cap_count" capacitances in parallel
def set_mimcap_um_rf_w_l(CL, cap_count):
    CL_per_cap = CL/float(cap_count)
    # for a mimcap_um_rf with l = 4u and w = 4u, capacitance is approximately = 35.2793 fF
    CL_ref = 35.2793e-15
    # let length and width of the capacitor be equal always
    cap_w_sqr = CL_per_cap/CL_ref
    cap_w = pow(cap_w_sqr, 0.5)
    # length and width of the capacitance are 4u*cap_w
    # Note: this calculation is an approximation and is off by some few 100s of fF from CL_per_cap value required
    return cap_w
# END of set_mimcap_um_rf_w_l()    
# below function sets the value of length and width of the capacitance element "mimcap"
# the RC tank contains "cap_count" capacitances in parallel
def set_mimcap_w_l(CL, cap_count):
    CL_per_cap = CL/float(cap_count)
    # for a mimcap with l = 2u and w = 2u, capacitance is approximately = 9.4724 fF
    CL_ref = 9.4724e-15
    # let length and width of the capacitor be equal always
    cap_w_sqr = CL_per_cap/CL_ref
    cap_w = pow(cap_w_sqr, 0.5)
    # length and width of the capacitance are 2u*cap_w
    # Note: this calculation is an approximation and is off by some few 100s of fF from CL_per_cap value required
    return cap_w
# END of set_mimcap_w_l()    

"""
===========================================================================================================================
-------------------------------------------- FUNCTIONS TO EDIT NETLIST FILE -----------------------------------------------
"""
# ---------------------------------------------- Netlists used in optimization --------------------------------------------
# ------------------------------------- updating global simulation parameters in netlist ----------------------------------
def global_netlist_edit(netlist_path, freq_array, RF_Bandwidth, pre_iteration_circuit_parameters, simulation_parameters):
    parameters_to_edit = copy.deepcopy(pre_iteration_circuit_parameters)
    # adding the flo and bandwidth and temperature varables also to the parameters to edit in the NF netlist
    # Integrated NF is carried out from Fif = 1K to Fif = Bandwidth
    parameters_to_edit['flo'] = freq_array[0]
    parameters_to_edit['flo_start'] = freq_array[0]
    parameters_to_edit['flo_stop'] = freq_array[-1]
    parameters_to_edit['Bandwidth'] = RF_Bandwidth
    parameters_to_edit['temperature'] = simulation_parameters['temp']
    parameters_to_edit['section'] = simulation_parameters['section']
    file_path = netlist_path
    with open(file_path, 'r') as file:
        scs_content = file.readlines()
        # print(scs_content)
        new_line = ""
        scs_new_content = list()
        for line in scs_content:
            line = line.strip()
            words = line.split(' ')
            word1 = words[-1].split('=')[0]
            if(words[0] == "parameters"):
                for param in parameters_to_edit:
                    if(word1 == param):
                        set_parameter = param + "=" + str(parameters_to_edit[param])
                        del(words[-1])
                        words.append(set_parameter)
                new_line = ' '.join(words)
                # print(new_line)
                scs_new_content.append(new_line + " \n")
            # adding the section detail that is the only different keyword from parameters in netlist that has to be set as well
            elif(word1 == "section"):
                set_section = "section=" + str(parameters_to_edit["section"])
                del(words[-1])
                words.append(set_section)
                new_line = ' '.join(words)
                scs_new_content.append(new_line + " \n")
            else:
                scs_new_content.append(line + " \n")
        # print(spice_new_content)
    with open(file_path, 'w') as file:
        file.writelines(scs_new_content)
# ------------------------------------------------------- S11 netlist -----------------------------------------------------
# newchange
def S11_netlist_edit(freq_array, RF_Bandwidth, pre_iteration_circuit_parameters, simulation_parameters, netlist_type):
    # simulation type is "sweep" or "single point"
    sweep = [
        ["psp_test", "psp", "sweeptype=absolute", "start=flo-Bandwidth", "stop=flo+Bandwidth", "step=freq_step"],
        ["+", "portharmsvec=[1]", "ports=[PORT0]", "annotate=status", "datatype=dbphase"]
    ]
    single_point = [
        ["psp_test", "psp", "sweeptype=absolute", "start=flo", "portharmsvec=[1]"],
        ["+", "ports=[PORT0]", "annotate=status", "datatype=dbphase"]
    ]
    parameters_to_edit = copy.deepcopy(pre_iteration_circuit_parameters)
    # adding the flo and bandwidth varables also to the parameters to edit in the S11 netlist
    # Single point S11 is carried out at frf = flo+Bandwidth
    parameters_to_edit['flo'] = freq_array[0]
    parameters_to_edit['flo_start'] = freq_array[0]
    parameters_to_edit['flo_stop'] = freq_array[-1]
    parameters_to_edit['Bandwidth'] = RF_Bandwidth
    parameters_to_edit['temperature'] = simulation_parameters['temp']
    parameters_to_edit['section'] = simulation_parameters['section']
    file_path = simulation_parameters['netlists']['S11_netlist']
    with open(file_path, 'r') as file:
        scs_content = file.readlines()
        # print(scs_content)
        new_line = ""
        scs_new_content = list()
        # variables for 
        flag = 0
        line_number = 0
        for line in scs_content:
            line = line.strip()
            words = line.split(' ')
            word1 = words[-1].split('=')[0]
            if(words[0] == "parameters"):
                for param in parameters_to_edit:
                    if(word1 == param):
                        set_parameter = param + "=" + str(parameters_to_edit[param])
                        del(words[-1])
                        words.append(set_parameter)
                new_line = ' '.join(words)
                # print(new_line)
                scs_new_content.append(new_line + " \n")
            # adding the section detail that is the only different keyword from parameters in netlist that has to be set as well
            elif(word1 == "section"):
                set_section = "section=" + str(parameters_to_edit["section"])
                del(words[-1])
                words.append(set_section)
                new_line = ' '.join(words)
                scs_new_content.append(new_line + " \n")
            elif(words[0]=="//" and words[1]=="PSP" and words[2]=="STATEMENTS"):
                flag = 1
                scs_new_content.append(line + " \n")
            elif flag==1:
                if netlist_type=="single_point":
                    new_line = ' '.join(single_point[line_number])
                else:
                    new_line = ' '.join(sweep[line_number])
                scs_new_content.append(new_line + " \n")
                if line_number==1:
                    flag = 0
                    # in this case, all the analysis statements for gain have been printed, we exit by setting flag=0
                else:
                    flag = 1
                    line_number = line_number + 1
            else:
                scs_new_content.append(line + " \n")
        # print(spice_new_content)
    with open(file_path, 'w') as file:
        file.writelines(scs_new_content)

# ------------------------------------------ END of S11_netlist_edit() ------------------------------------------------

# ------------------------------------------------ gain netlist -------------------------------------------------------
def gain_netlist_edit(simulation_parameters, netlist_type):
    # netlist_type can be "single_point" or "sweep"
    # gain is carried out at frf = flo+Bandwidth for single point and from start=flo-Bandwidth to stop=flo+Bandwidth for "sweep"
    single_point = [
        ["pac_test", "pac", "sweeptype=absolute", "start=flo+Bandwidth", "maxsideband=10"],
        ["+", "annotate=status"]
    ]
    sweep = [
        ["pac_test", "pac", "sweeptype=absolute", "start=flo+1K", "stop=flo+Bandwidth", "step=freq_step"],
        ["+", "maxsideband=10", "annotate=status"]
    ]
    file_path = simulation_parameters['netlists']['pss_netlist']
    with open(file_path, 'r') as file:
        scs_content = file.readlines()
        # print(scs_content)
        new_line = ""
        scs_new_content = list()
        flag = 0
        line_number = 0
        for line in scs_content:
            line = line.strip()
            words = line.split(' ')
            word1 = words[-1].split('=')[0]
            # adding the PAC statements based on whether the simulation is sweep or single-point
            if(words[0]=="//" and words[1]=="PAC" and words[2]=="STATEMENTS"):
                flag = 1
                scs_new_content.append(line + " \n")
            elif flag==1:
                if netlist_type=="single_point":
                    new_line = ' '.join(single_point[line_number])
                else:
                    new_line = ' '.join(sweep[line_number])
                scs_new_content.append(new_line + " \n")
                if line_number==1:
                    flag = 0
                    # in this case, all the analysis statements for gain have been printed, we exit by setting flag=0
                else:
                    flag = 1
                    line_number = line_number + 1
            else:
                scs_new_content.append(line + " \n")
        # print(spice_new_content)
    with open(file_path, 'w') as file:
        file.writelines(scs_new_content)

# --------------------------------------- END of gain_netlist_edit() ---------------------------------------------

# ---------------------------------------------- NF netlist ------------------------------------------------------
def integrated_NF_netlist_edit(freq, RF_Bandwidth, pre_iteration_circuit_parameters, simulation_parameters):
    parameters_to_edit = copy.deepcopy(pre_iteration_circuit_parameters)
    # adding the flo and bandwidth and temperature varables also to the parameters to edit in the NF netlist
    # Integrated NF is carried out from Fif = 1K to Fif = Bandwidth
    parameters_to_edit['flo'] = freq
    parameters_to_edit['Bandwidth'] = RF_Bandwidth
    parameters_to_edit['temperature'] = simulation_parameters['temp']
    parameters_to_edit['section'] = simulation_parameters['section']
    file_path = simulation_parameters['netlists']['pss_netlist']
    with open(file_path, 'r') as file:
        scs_content = file.readlines()
        # print(scs_content)
        new_line = ""
        scs_new_content = list()
        for line in scs_content:
            line = line.strip()
            words = line.split(' ')
            word1 = words[-1].split('=')[0]
            if(words[0] == "parameters"):
                for param in parameters_to_edit:
                    if(word1 == param):
                        set_parameter = param + "=" + str(parameters_to_edit[param])
                        del(words[-1])
                        words.append(set_parameter)
                new_line = ' '.join(words)
                # print(new_line)
                scs_new_content.append(new_line + " \n")
            # adding the section detail that is the only different keyword from parameters in netlist that has to be set as well
            elif(word1 == "section"):
                set_section = "section=" + str(parameters_to_edit["section"])
                del(words[-1])
                words.append(set_section)
                new_line = ' '.join(words)
                scs_new_content.append(new_line + " \n")
            else:
                scs_new_content.append(line + " \n")
        # print(spice_new_content)
    with open(file_path, 'w') as file:
        file.writelines(scs_new_content)

# --------------------------------------- END of integrated_NF_netlist_edit() ------------------------------------------

# -------------------------------------------------- iip3 netlist ------------------------------------------------------
def iip3_netlist_edit(freq, pre_iteration_circuit_parameters, simulation_parameters):
    parameters_to_edit = copy.deepcopy(pre_iteration_circuit_parameters)
    # adding the flo, frf1, frf2, prf, prf range and step variables also to the parameters to edit in the iip3 netlist
    parameters_to_edit['flo'] = freq
    parameters_to_edit['frf1'] = freq + simulation_parameters['iip3']['tone 1']
    parameters_to_edit['frf2'] = freq + simulation_parameters['iip3']['tone 2']
    parameters_to_edit['prf'] = simulation_parameters['iip3']['prf']
    parameters_to_edit['prf_min'] = simulation_parameters['iip3']['prf_min']
    parameters_to_edit['prf_max'] = simulation_parameters['iip3']['prf_max']
    parameters_to_edit['prf_step'] = simulation_parameters['iip3']['prf_step']
    parameters_to_edit['temperature'] = simulation_parameters['temp']
    parameters_to_edit['section'] = simulation_parameters['section']
    file_path = simulation_parameters['netlists']['iip3_netlist']

    with open(file_path, 'r') as file:
        scs_content = file.readlines()
        # print(scs_content)
        new_line = ""
        scs_new_content = list()
        for line in scs_content:
            line = line.strip()
            words = line.split(' ')
            word1 = words[-1].split('=')[0]
            if(words[0] == "parameters"):
                for param in parameters_to_edit:
                    if(word1 == param):
                        set_parameter = param + "=" + str(parameters_to_edit[param])
                        del(words[-1])
                        words.append(set_parameter)
                new_line = ' '.join(words)
                # print(new_line)
                scs_new_content.append(new_line + " \n")
            # adding the section detail that is the only different keyword from parameters in netlist that has to be set as well
            elif(word1 == "section"):
                set_section = "section=" + str(parameters_to_edit["section"])
                del(words[-1])
                words.append(set_section)
                new_line = ' '.join(words)
                scs_new_content.append(new_line + " \n")
            else:
                scs_new_content.append(line + " \n")
        # print(spice_new_content)
    with open(file_path, 'w') as file:
        file.writelines(scs_new_content)
    
# --------------------------------------------- END of iip3_netlist_edit() ------------------------------------------------
"""
===========================================================================================================================
-------------------------------------------- FUNCTIONS TO RUN SPECTRE NETLIST ---------------------------------------------
"""
def run_spectre(netlist_path):
    input_netlist_path = netlist_path
    # defining the spectre command
    spectre_command = "spectre " + netlist_path + " =log log.txt"
    # running the spectre command
    os.system(spectre_command)

# ------------------------- END of run_spectre() -----------------------------

def run_spectre_with_PSF_file(netlist_path):
    input_netlist_path = netlist_path
    # defining the spectre command
    spectre_command = "spectre " + netlist_path + " +escchars +log ./psf/spectre.out -format psfxl -raw ./psf ++aps +lqtimeout 900 -maxw 5 -maxn 5"
    # the above command will generate a psf file in the same directory as the netlist 
    # The psf file contains all the simulation results 
    # running the spectre command
    os.system(spectre_command)

# ------------------------- END of run_spectre_with_PSF_file() -----------------------------

"""
===========================================================================================================================
-------------------------------------------- FUNCTIONS TO READ .OUT FILE --------------------------------------------------
"""
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
# ---------------------------------------- extracting S11 from sp.out file ------------------------------------------------
def extract_S11(ocean_script):
    # to extract s11 onto a csv file named s11.csv run the ocean script
    ocean_command = "ocean -restore " + ocean_script
    os.system(ocean_command)
    freq_list = []
    S11_db_list = []
    CSV_file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/s11.csv"
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
                freq_list.append(float(row[i]))
                # we are interested in the absolute value of S11, because S11 needs to be as close to 0 as possible
                S11_db_list.append(abs(float(row[i+1])))
    return freq_list, S11_db_list
# --------------------------------------------- END of extract_S11() ------------------------------------------------------

# --------------------------------------- extracting gain using ocean script ----------------------------------------------
def extract_gain(ocean_script, netlist_type):
    # gain can be a "single_point" simulation or "sweep" - we extract the details accordingly
    if netlist_type=="single_point":
        # run the ocean script to write data onto results.txt file
        # used ocean_script = "extract_single_point_gain.ocn"
        ocean_command = "ocean -restore " + ocean_script
        os.system(ocean_command)
        # results.txt file path
        results_path = "/home/ee20b087/cadence_project/BTP_EE20B087/results.txt"
        D = []
        with open(results_path, 'r') as f:
            for line in f:
                row = [item.strip() for item in line.split()]
                D.append(row)
        # for a single point pac analysis the value of D[0][0] has the gain in dB
        # deleting the results file
        delete_command = "rm /home/ee20b087/cadence_project/BTP_EE20B087/results.txt"
        os.system(delete_command)
        return float(D[0][0])
    else:
        # run ocean script that writes frequency swept .pac analysis data to .csv file
        # used ocean_script = "extract_sweep_gain.ocn"
        ocean_command = "ocean -restore " + ocean_script
        os.system(ocean_command)
        # results are stored in freq_analysis_gain.csv
        CSV_file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/freq_analysis_gain.csv"
        freq_list, gain_db_list = read_CSV(CSV_file_path)
        return freq_list, gain_db_list
# --------------------------------------------- END of extract_gain() -----------------------------------------------------

# ----------------------------------------- extracting NF using ocean script ----------------------------------------------
# we need to read the psf file using ocean script to get the gain, noise and other than S11 parameters
def extract_integrated_NF(ocean_script, return_freq_data):
    # if return_freq_data is True, then the data points of noise figure vs frequency will be read from csv file and returned by function
    # run the ocean script to write data onto results.txt file
    # used ocean_script = "extract_NF.ocn"
    ocean_command = "ocean -restore " + ocean_script
    os.system(ocean_command)
    # results.txt file path
    results_path = "/home/ee20b087/cadence_project/BTP_EE20B087/results.txt"
    D = []
    with open(results_path, 'r') as f:
        for line in f:
            row = [item.strip() for item in line.split()]
            D.append(row)
    # for noise figure .pnoise analysis the value of D[0][0] has the integrated SSB NF in dB
    # deleting the results file
    delete_command = "rm /home/ee20b087/cadence_project/BTP_EE20B087/results.txt"
    os.system(delete_command)
    if return_freq_data==True:
        CSV_file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/freq_analysis_NF.csv"
        freq_list, NF_db_list = read_CSV(CSV_file_path)
        return float(D[0][0]), freq_list, NF_db_list
    else:
        return float(D[0][0])
# ----------------------------------------- END of extract_integrated_NF() ------------------------------------------------

# --------------------------------------- extracting iip3 using ocean script ----------------------------------------------
# Function to extract iip3 from "hb" analysis - 
# In this function, first we find the derivative of the third order harmonic curve to find the correct extrapolation point for the 3dB/dB line
# Based on the correct extrapolation point, we use ocean commands (ocean script) to extract the iip3 spec into the text file
def extract_iip3(ocean_scripts):
    # there are 2 ocean scripts - 
    #   1) to find the slope of the 3rd order harmonic curve and write the waveform to a CSV file
    #   2) to plug in the calculated value of the extrapolation point for the 3rd order curve into the ipn command and find the iip3 spec
    # obtaining the path of both ocean scripts
    write_ip3_slope_to_CSV_path = ocean_scripts['write_ip3_slope_to_CSV_path']
    extract_iip3_post_optimization_path = ocean_scripts['extract_iip3_post_optimization_path']
    ocean_command = "ocean -restore " + write_ip3_slope_to_CSV_path
    # run the first ocean script to write the slope waveform to the csv file - "slope_ip3_curve.csv"
    os.system(ocean_command)
    CSV_file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/slope_ip3_curve.csv"
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

    # Print or use x and y values as needed
    # Note: the input power where the slope is closest to 3dB/dB is selected as the extrapolation point
    slope_error = np.abs(np.array(y_values)-3)
    index = np.where(slope_error == np.min(slope_error))[0]
    extrapolation_point = str(np.array(x_values)[index][0])

    # Now, using the extrapolation point, we run the ocean script that return the iip3 spec to a text file - "results.txt"
    with open(extract_iip3_post_optimization_path, 'r') as file:
        ocn_content = file.readlines()
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

    with open(extract_iip3_post_optimization_path, 'w') as file:
	    file.writelines(ocn_new_content)
    # after editing the ocean script with the correct extrapolation pt in the ipn function, we run the script,
    ocean_command = "ocean -restore " + extract_iip3_post_optimization_path
    os.system(ocean_command)

    # reading "results.txt" to return iip3 spec
    results_path = "/home/ee20b087/cadence_project/BTP_EE20B087/results.txt"
    D = []
    with open(results_path, 'r') as f:
        for line in f:
            row = [item.strip() for item in line.split()]
            D.append(row)
    # the value of D[0][0] has the input referred ip3 point in dBm
    # deleting the results file
    delete_command = "rm /home/ee20b087/cadence_project/BTP_EE20B087/results.txt"
    os.system(delete_command)
    return float(D[0][0])
# --------------------------------------------- END of extract_iip3() -----------------------------------------------------
# ------------------------------------------------ extract results --------------------------------------------------------
def extract_results(ocean_script):
    # run the ocean script to write data onto three different csv files for gain, NF and s11
    # used ocean_script = "extract_result.ocn" and "extract_s11.ocn" 
    ocean_command = "ocean -restore " + ocean_script
    os.system(ocean_command)
    # gain results are stored in gain.csv
    CSV_file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/gain.csv"
    freq_list, gain_db_list = read_CSV(CSV_file_path)
    # NF results are stored in NF.csv
    CSV_file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/NF.csv"
    freq_list, NF_db_list = read_CSV(CSV_file_path)
    # in s11.csv alone all the data is stored in one single row in the format x,y
    # so we use different code to extract it alone
    
    return freq_list, gain_db_list, NF_db_list

"""
===========================================================================================================================
-------------------------------------- FUNCTIONS TO PRINT STATEMENTS/SAVE OUTPUTS -----------------------------------------
"""
# Function to write the results to a file is given below
def write_opt_results(loss_iter, post_iteration_circuit_parameters_iter, simulated_output_parameters_iter, alpha, iter_number):
    if iter_number == 1:
        os.system("rm /home/ee20b087/cadence_project/BTP_EE20B087/opt_results.txt")
    
    file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/opt_results.txt"
    with open(file_path, 'a') as file:
        file_content = list()
        words = ["iteration:", str(iter_number)]
        line = ' '.join(words)
        file_content.append(line + " \n")
        words = ["alpha (learning rate):", str(alpha)]
        line = ' '.join(words)
        file_content.append(line + " \n")
        words = ["loss:", str(loss_iter['loss']), "loss_S11:", str(loss_iter['loss_S11']), "loss_gain:", str(loss_iter['loss_gain']), "loss_NF:", str(loss_iter['loss_NF']), "loss_iip3:", str(loss_iter['loss_iip3'])]
        line = ' '.join(words)
        file_content.append(line + " \n")
        words = [
            "simulated output parameters-->",
            "S11:", str(simulated_output_parameters_iter['S11_db']), 
            "gain:", str(simulated_output_parameters_iter['gain_db']), 
            "NF:", str(simulated_output_parameters_iter['NF_db']),
            "iip3:", str(simulated_output_parameters_iter['iip3'])
            ]
        line = ' '.join(words)
        file_content.append(line + " \n")
        words = [
            "post iteration circuit parameters-->",
            "Resistance width:", str(post_iteration_circuit_parameters_iter['res_w']), 
            "capacitance width:", str(post_iteration_circuit_parameters_iter['cap_w']), 
            "sw_mul:", str(post_iteration_circuit_parameters_iter['sw_mul'])
            ]
        line = ' '.join(words)
        file_content.append(line + " \n")
        file.writelines(file_content)
    # END file writing
# END of write_opt_results()


# Print the output simulated parameters after each iteration
def print_post_iteration(loss_iter, post_iteration_circuit_parameters_iter, iter_number, print_type):
    # print type gives choice of what the user wants to print
    # print type = 1 
    #   only print the loss_iter
    # print type = 2 
    #   print loss and post_iteration_ciruit parameters of each iteration
    if print_type == 1:
        print('iter: ', iter_number)
        print('loss: ', loss_iter[iter_number]['loss'], ' loss_S11: ', loss_iter[iter_number]['loss_S11'])
    elif print_type == 2:
        print('iter: ', iter_number)
        print('loss: ', loss_iter[iter_number]['loss'], ' loss_S11: ', loss_iter[iter_number]['loss_S11'])
        print('post iteration circuit parameters: ', post_iteration_circuit_parameters_iter[iter_number])
    # END of if-else
# END of print_post_iteration()
"""
===========================================================================================================================
---------------------------------------- FUNCTIONS TO PLOT OUTPUTS WITH MATPLOTLIB ----------------------------------------
"""
def plot_result(freq_list, output_data_list, xlabel, ylabel, title, plot_type):
    #plt.style.use('_mpl-gallery')
    x = freq_list
    y = output_data_list
    xmin = freq_list[0]
    xmax = freq_list[-1]
    ymin = min(output_data_list)
    ymax = max(output_data_list)

    print("-------------------------------- Close the current plot to view the next plot ----------------------------------\n")
    # things to be present in each plot:
    #   title, xlabel, ylabel, xlim(min and max), ylim(min and max)
    # plot can be "linear" or "semilogx" type 
    if plot_type == "linear":
        fig, ax = plt.subplots()
        ax.plot(x, y, linewidth=2.0, linestyle='solid', color='blue')
        ax.grid()

        ax.set(xlim=(xmin, xmax), ylim=(ymin-0.5, ymax+0.5), xticks=np.linspace(xmin, xmax, 21),
            xlabel=xlabel, ylabel=ylabel, title=title
            )
        plt.show()
    # END if
    else:
        fig, ax = plt.subplots()
        ax.semilogx(x, y, linewidth=2.0, linestyle='solid', color='blue')
        ax.grid()

        ax.set(xlim=(xmin, xmax), ylim=(ymin-0.1, ymax+0.1), xticks=np.logspace(np.log10(xmin), np.log10(xmax), 5),
            xlabel=xlabel, ylabel=ylabel, title=title
            )
        plt.show()
    # END else
# END plot_result()
