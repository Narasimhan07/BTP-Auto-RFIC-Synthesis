# ======================================= Hand calculations for Voltage mode Passive mixer ================================================
# Circuit parameters for hand calculation:
# Switch resistance: Rsw
# (Rsw is decided by the number of fingers and multiplier of the switching NMOS RF)
# Load capacitance: CL
# Resistance parallel to load capacitance: RB
# Port resistance: Rs
# contents of input_circuit_specs(dictionary) - min_LO_freq, max_LO_freq, gain, S11, NF, power consumption
# contents of initial circuit parameters(dictionary) - cap_w, res_w, switch NMOS{sw_fin, sw_mul}, switch_w, w_per_fin

import os
import numpy as np
import common_functions as cf

def hand_calculation(output_conditions, hand_calculated_circuit_parameters):
    # We set a value for the switch resistance; Corresponding number of fingers to approximate Rsw will be chosen later
    Rsw = 5
    f_min = output_conditions['min_LO_freq']
    f_max = output_conditions['max_LO_freq']
    # We define variable RB, Rs and CL that will be assigned to the respective 'keys' in the hand_calculated_circuit_parameters dictionary
    Rs = 50
    # hand_calculated_circuit_parameters['Port impedance'] = Rs // not required in the initial circuit parameters
    # port resistance has been set to 50 ohms
    Rs_eff = Rs + Rsw
    gamma = 2/pow(np.pi,2)
    # We define a hypothetical resistance Rsh (shunt resistance) which aids in computing the value of RB for input impedance matching
    Rsh = ((4*gamma)/(1-4*gamma))*Rs_eff
    # Now using gamma, Rsh, Rsw and Rs we compute the RB value for Zin=50 (when Flo~Frf)
    RB = (1/gamma)*((Rsh*Rs - Rsw*Rsh)/(Rsw + Rsh - Rs))
    # assigning the computed value of res_w from RB
    hand_calculated_circuit_parameters['res_w'] = cf.set_rppoly_rf_w(RB)

    # Performing hand calculation for CL
    # we make use of f_min and f_max to compute the limits on CL
    # Case 1: When switch is on ---> gives upper limit of CL
    CL_max = 1/(f_max*Rsw)
    # Case 2: When switch is off ---> gives lower limit of CL
    # We are mainly focussing at the f_min region: the off resistance of the switch >> RB
    # This renders effective RB ~ RB
    CL_min = 1/(f_min*RB)
    # We set CL to be 1.5 times CL_min and also check if it is atleast 2.5 times smaller than CL_max
    a = 1.5
    CL = a*CL_min
    while 2.5*CL>CL_max:
        a = a-0.05
        CL = a*CL_min
    # Setting cap_w using the CL calculated value
    hand_calculated_circuit_parameters['cap_w'] = cf.set_mimcap_um_rf_w_l(CL)

    # now we approximate the value of sw_fin and sw_mul that gives us the required Rsw
    file_path = "/home/ee20b087/cadence_project/BTP_EE20B087/switch_resistance.scs"
    # setting the frequency at which switch resistance is analysed as f = ( f_min + f_max )/2
    f = 0.5*(f_max + f_min)
    # multiplier for the nmos switch
    mul = 2
    # the number of fingers need to be swept from min_fingers to max_fingers
    min_fingers = 10
    max_fingers = 50
    parameter_to_edit = ['f','min_fingers','max_fingers','mul']
    parameter_value = {'f':f,'min_fingers':min_fingers,'max_fingers':max_fingers,'mul':mul}

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
    spectre_command = "spectre switch_resistance.scs =log log.txt"
    os.system(spectre_command)
    # Now we read the ac.out file to find out the nfin that closest approximates the Rsw value
    with open("/home/ee20b087/cadence_project/BTP_EE20B087/ac.out",'r') as f:
        file_content = f.readlines()
        start = False
        for line in file_content:
            line = line.strip()
            words = line.split(' ')
        
            if(words[0] == str(min_fingers)):
                start = True
                # we define a variable nmos_ron the stores the on resistance 
                nmos_ron = float(words[-1])
                nfin = float(words[0])
                continue
            if(start):
                if(abs(float(words[-1]) - Rsw)<abs(nmos_ron - Rsw)):
                    # if the absolute difference in nmos_ron and Rsw is lesser than the previous iteration, nmos_ron value is replaced
                    nmos_ron = float(words[-1])
                    nfin = float(words[0])
                if(words[0] == str(max_fingers)):
                    start = False
                else:
                    continue
    hand_calculated_circuit_parameters['sw_fin'] = nfin
    hand_calculated_circuit_parameters['sw_mul'] = mul
    w_per_fin = 1e-6
    hand_calculated_circuit_parameters['w_per_fin'] = w_per_fin
    effective_switch_width = nfin*w_per_fin
    hand_calculated_circuit_parameters['switch_w'] = effective_switch_width