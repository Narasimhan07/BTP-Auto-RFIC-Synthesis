# ======================================= Hand calculations for Current mode Passive mixer ================================================
# Circuit parameters for hand calculation:
# Switch resistance: Rsw
# (Rsw is decided by the number of fingers and multiplier of the switching NMOS RF)
# Resistance of transimpedance amplifier: RL
# Capacitance of the transimpedance amplifier: CL
# Port resistance: Rs
# contents of input_circuit_specs(dictionary) - min_LO_freq, max_LO_freq, RF_Bandwidth, transimpedance gain (ohms), S11, NF, iip3,
#       other details that are fixed in the circuit: gain of the OPAMP in TIA, transconductance gain of the VCCS(LNA), ouput impedance of VCCS(LNA) 
# contents of initial circuit parameters(dictionary) - res_w, cap_w, switch NMOS{sw_fin, sw_mul}, switch_w, w_per_fin, G, RN, gm

import os
import numpy as np
import Passive_Mixer_CM.common_functions as cf

def hand_calculation(output_conditions, hand_calculated_circuit_parameters):
    # We set a value for the switch resistance; Corresponding number of fingers to approximate Rsw will be chosen later
    Rsw = 5
    f_min = output_conditions['min_LO_freq']
    f_max = output_conditions['max_LO_freq']
    # We define variable RB, Rs and CL that will be assigned to the respective 'keys' in the hand_calculated_circuit_parameters dictionary
    Rs = 50
    # hand_calculated_circuit_parameters['Port impedance'] = Rs // not required in the initial circuit parameters
    # port resistance has been set to 50 ohms
    # define RN as the output impedance of the LNA (output of the LNA is a current, like a VCCS and RN is like the norton resistance)
    RN = output_conditions['RN']
    hand_calculated_circuit_parameters['RN'] = RN
    # defining the Transimpedance gain of the TIA as G and transconductance of the LNA as gm
    G = output_conditions['G']
    hand_calculated_circuit_parameters['G'] = G
    gm = output_conditions['gm']
    hand_calculated_circuit_parameters['gm'] = gm
    # setting RL as 3000 ohms
    RL = 3e3
    #hand_calculated_circuit_parameters['RL'] = RL
    #assigning the computed value of res_w from RL
    hand_calculated_circuit_parameters['res_w'] = cf.set_rppoly_rf_w(RL, 5)

    # Performing hand calculation for CL
    # setting CL to 10pF
    CL = 10e-12
    # hand_calculated_circuit_parameters['CL'] = CL
    hand_calculated_circuit_parameters['cap_w'] = cf.set_mimcap_w_l(CL, 3)
    # now we approximate the value of sw_fin and sw_mul that gives us the required Rsw
    file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/switch_resistance.scs"
    # setting the frequency at which switch resistance is analysed as f = ( f_min + f_max )/2
    f = 0.5*(f_max + f_min)
    # multiplier for the nmos switch
    # the number of fingers is 1
    nfin=1
    # the width of the mosfet is 1u and total width = width*sw_mul
    wn=1e-6
    # the multiplier need to be swept from min_mul to max_mul
    # the number of fingers need to be swept from min_fingers to max_fingers
    # the switch resistance is approximated at some particular temperature
    min_mul = 30
    max_mul = 120
    temperature = 27
    parameter_to_edit = ['f','min_mul','max_mul','nfin', 'temperature', 'wn']
    parameter_value = {'f':f,'min_mul':min_mul,'max_mul':max_mul,'nfin':nfin, 'temperature':temperature, 'wn':wn}

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
                for parameter in parameter_to_edit:
                    if(word1 == parameter):
                        set_parameter = parameter + "=" + str(parameter_value[parameter])
                        del(words[-1])
                        words.append(set_parameter)
                new_line = ' '.join(words)
                # print(new_line)
                scs_new_content.append(new_line + " \n")
            else:
                scs_new_content.append(line + " \n")
        # print(spice_new_content)
    with open(file_path, 'w') as file:
        file.writelines(scs_new_content)
    # The switch_resistance.scs is simulated and ac.out is read to find the suitable value for sw_fin and sw_mul
    spectre_command = "spectre " + file_path + " =log log.txt"
    os.system(spectre_command)
    # Now we read the ac.out file to find out the nfin that closest approximates the Rsw value
    with open("/home/ee20b087/cadence_project/BTP_EE20B087/ac.out",'r') as f:
        file_content = f.readlines()
        start = False
        for line in file_content:
            line = line.strip()
            words = line.split(' ')
        
            if(words[0] == str(min_mul)):
                start = True
                # we define a variable nmos_ron the stores the on resistance 
                nmos_ron = float(words[-1])
                mul = float(words[0])
                continue
            if(start):
                if(abs(float(words[-1]) - Rsw)<abs(nmos_ron - Rsw)):
                    # if the absolute difference in nmos_ron and Rsw is lesser than the previous iteration, nmos_ron value is replaced
                    nmos_ron = float(words[-1])
                    mul = float(words[0])
                if(words[0] == str(max_mul)):
                    start = False
                else:
                    continue
    # setting the multiplier and width of nmos            
    hand_calculated_circuit_parameters['sw_mul'] = mul
    hand_calculated_circuit_parameters['sw_wn'] = wn
    # total width of the switch = sw_mul*sw_wn
    switch_w = mul*wn
    hand_calculated_circuit_parameters['switch_w'] = switch_w
    # for determining the load capacitance presented by the switch, 
    # capacitance per unit um width is = 1 fF/um
    load_cap = switch_w*(1e-15/1e-6)
    # setting the starting value of rho = 2
    hand_calculated_circuit_parameters['rho'] = 2.0
    # adding the inverters details below
    # the variables related to the inverter chain are:
    # 1. the number of inverters = N
    # 2. the ratio of inverter size = rho
    # 3. for each inverter: wp, wn, mp, mn and wp_total = wp*mp, wn_total = wn*mn
    N, wp_total, wn_total, wp, wn, mp, mn = cf.buffer_block(hand_calculated_circuit_parameters['rho'], load_cap)
    hand_calculated_circuit_parameters['N'] = N
    i=0
    while i < N:
        str1 = "wp" + str(i) + "_total"
        str2 = "wn" + str(i) + "_total"
        str3 = "wp" + str(i) 
        str4 = "wn" + str(i)
        str5 = "mp" + str(i)
        str6 = "mn" + str(i)
        hand_calculated_circuit_parameters[str1] = wp_total[i]
        hand_calculated_circuit_parameters[str2] = wn_total[i]
        hand_calculated_circuit_parameters[str3] = wp[i]
        hand_calculated_circuit_parameters[str4] = wn[i]
        hand_calculated_circuit_parameters[str5] = mp[i]
        hand_calculated_circuit_parameters[str6] = mn[i]
        i = i + 1
# END of hand_calculations for sw_mul, res_w and cap_w in VM Passive mixer and buffer block variables