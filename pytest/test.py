# import csv
# import numpy as np
# CSV_file_path = "/Users/sreyas/Documents/BTP_EE20B087/pytest/s11.csv"
# # the extracted points from csv are x-axis:input power in dbm and y-axis:slope of the 3rd harmonic plot 
# x_values = []
# y_values = []

# # Open the CSV file
# with open(CSV_file_path) as csvfile:
#     # Create a CSV reader
#     csv_reader = csv.reader(csvfile)
#     # Skip the header row
#     next(csv_reader)
#     # Iterate over each row in the CSV file
#     for row in csv_reader:
#         i = 0
#         for i in range(0,len(row), 2):
#             x_values.append(float(row[i]))
#             y_values.append(float(row[i+1]))
# print(x_values)
# print(y_values)
# -----------------------------------------------
# import math
# def round_off_fun(x):
#     if x>0:
#         y = x - int(x)
#         if y>=0.5:
#             return float(int(x) + 1)
#         else:
#             return float(int(x))
#     else:
#         y = x - int(x)
#         if y<=-0.5:
#             return float(int(x) - 1)
#         else:
#             return float(int(x))
# def buffer_block(rho, load_cap):
#     # number of inverters = N
#     y = math.log((load_cap/4.17), rho)
#     if (round_off_fun(y))%2 == 1:
#         if y - round_off_fun(y) >= 0:
#             N = round_off_fun(y) + 1
#         else:
#             N = round_off_fun(y) - 1
#     else:
#         N = round_off_fun(y)
#     print(N)
# buffer_block(2, 100)
# -----------------------------------
import numpy as np 
import copy
netlist_path = "/Users/sreyas/Documents/BTP_EE20B087/pytest/test_netlist.scs"
pre_iteration_circuit_parameters = {
    'res_w':1,
    'cap_w':1,
    'sw_mul':1,
    'switch_w':1,
    'sw_wn':1e-6,
    'rho':2,
    'N':4,
    'wp0':1,
    'wp0_total':2,
    'mp0':2,
    'wn0':1,
    'wn0_total':2,
    'mn0':2,
    'wp1':1,
    'wp1_total':2,
    'mp1':2,
    'wn1':1,
    'wn1_total':2,
    'mn1':2,
    'wp2':1,
    'wp2_total':2,
    'mp2':2,
    'wn2':1,
    'wn2_total':2,
    'mn2':2,
    'wp3':1,
    'wp3_total':2,
    'mp3':2,
    'wn3':1,
    'wn3_total':2,
    'mn3':2,

}
freq_array = np.linspace(100e6, 1e9, 3)
RF_Bandwidth = 10e6
simulation_parameters = {
    'section':"ff_lib",
    'temp':50
}
def global_netlist_edit(netlist_path, freq_array, RF_Bandwidth, pre_iteration_circuit_parameters, simulation_parameters):
    parameters_to_edit = copy.deepcopy(pre_iteration_circuit_parameters)
    N = parameters_to_edit['N']
    parameters_flag = 0
    buffer_block_flag = 0
    write_buffer_block = 1
    # adding the flo and bandwidth and temperature varables also to the parameters to edit in the netlist
    # Integrated NF is carried out from Fif = 1K to Fif = Bandwidth
    parameters_to_edit['flo'] = freq_array[0]
    parameters_to_edit['flo_start'] = freq_array[0]
    parameters_to_edit['flo_stop'] = freq_array[-1]
    parameters_to_edit['Bandwidth'] = RF_Bandwidth
    parameters_to_edit['temperature'] = simulation_parameters['temp']
    #parameters_to_edit['section'] = simulation_parameters['section']
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
            # adding all the circuit parameter variables and simulation parameter variables below
            if(words[0] == "//" and words[1] == "PARAMETERS"):
                parameters_flag = 1
                scs_new_content.append(line + " \n")
            elif(words[0] == "parameters"):
                if parameters_flag == 1:
                    for param in parameters_to_edit:
                        set_parameter = param + "=" + str(parameters_to_edit[param])
                        new_words = ["parameters", set_parameter]
                        new_line = ' '.join(new_words)
                        scs_new_content.append(new_line + " \n")
                    parameters_flag = 0
                else:
                    continue
            # adding the section detail that is the only different keyword from parameters in netlist that has to be set as well
            elif(word1 == "section"):
                set_section = "section=" + str(simulation_parameters["section"])
                del(words[-1])
                words.append(set_section)
                new_line = ' '.join(words)
                scs_new_content.append(new_line + " \n")
            elif(words[0] == "subckt" and words[1] == "buffer_block"):
                buffer_block_flag = 1
                scs_new_content.append(line + " \n")
            elif buffer_block_flag == 1:
                if write_buffer_block == 1:
                    i = N-1
                    while i >= 0:
                        if i == 0:
                            new_words = ["I0", "(Vdd In w0)", "Inverter", "wn=wn0", "muln=mn0", "wp=wp0", "mulp=mp0"]
                        elif i == N-1:
                            new_words = ["I" + str(i), "(Vdd w" + str(i-1) + " Out)", "Inverter", "wn=wn" + str(i), "muln=mn" + str(i), "wp=wp" + str(i), "mulp=mp" + str(i)]
                        else:
                            new_words = ["I" + str(i), "(Vdd w" + str(i-1) + " w" + str(i) + ")", "Inverter", "wn=wn" + str(i), "muln=mn" + str(i), "wp=wp" + str(i), "mulp=mp" + str(i)]
                        new_line = ' '.join(new_words)
                        scs_new_content.append(new_line + " \n ")
                        i = i - 1
                    # END while loop to write inverter lines
                    # setting write_buffer_block flag 0 since lines are written
                    write_buffer_block = 0
                else:
                    # if the buffer block is written, don't write anything in new file till endckt is reached
                    if(words[0] == "ends" and words[1] == "buffer_block"):
                        buffer_block_flag = 0
                        scs_new_content.append(line + " \n")
                    else:
                        continue
            else:
                scs_new_content.append(line + " \n")
        # print(spice_new_content)
    with open(file_path, 'w') as file:
        file.writelines(scs_new_content)
# END definition
global_netlist_edit(netlist_path, freq_array, RF_Bandwidth, pre_iteration_circuit_parameters, simulation_parameters)