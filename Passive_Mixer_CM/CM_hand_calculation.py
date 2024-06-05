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
    Rsw = 3
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
    # setting RL as 1000 ohms
    RL = 1e3
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
    fingers = 1
    # the number of fingers need to be swept from min_fingers to max_fingers
    # the switch resistance is approximated at some particular temperature
    min_mul = 10
    max_mul = 60
    temperature = 27
    parameter_to_edit = ['f','min_mul','max_mul','fingers', 'temperature']
    parameter_value = {'f':f,'min_mul':min_mul,'max_mul':max_mul,'nfin':fingers, 'temperature':temperature}

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
    hand_calculated_circuit_parameters['sw_mul'] = mul
