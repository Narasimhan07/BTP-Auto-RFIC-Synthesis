# ======================================= Main Program for CM Passive Mixer =====================================================
# In this file: All the simulation, circuit, output parameters required for optimization of the mixer circuit is defined
# class 'Circuit' object is created and,
# The full_optimization function is called.
import os
import numpy as np
import copy
import matplotlib.pyplot as plt 
import Passive_Mixer_CM.CM_hand_calculation as cm_hc
import Passive_Mixer_CM.full_optimization as fo 
import Passive_Mixer_CM.gradient_descent as gd 
# importing the analysis scripts for post optimization analysis
import Passive_Mixer_CM.frequency_analysis as fa
import Passive_Mixer_CM.temperature_analysis as ta
import Passive_Mixer_CM.process_corners as pc
"""
===========================================================================================================================
---------------------------------------- FUNCTIONS TO INITIALIZE DICTIONARIES ---------------------------------------------
"""
def get_output_conditions(CM_passive_mixer):
    CM_passive_mixer['output_conditions'] = {
        'min_LO_freq':100e6, 
        'max_LO_freq':1e9, 
        'RF_Bandwidth':10e6, 
        # the below three parameters are fixed circuit parameters namely
        #   G = gain of the OPAMP in the TIA
        #   gm = transconductance of the LNA
        #   RN = norton resistance (output resistance) of the LNA
        'RN':250,
        'G':100,
        'gm':40e-3,
        # the gain is from the input of the VCCS to the differential output of the mixer
        'gain_db':60, 
        'S11_db':0, 
        'NF_db':8,
        'iip3':10
    }
# END of get_output_conditions()

def get_simulation_conditions(CM_passive_mixer):
    # defining the name of netlists files for simulating the output parameters
    # edit netlists in the lines below and uncomment the required lines
    CM_passive_mixer['simulation'] = {}
    CM_passive_mixer['simulation']['temp'] = 27
    CM_passive_mixer['simulation']['Vdd'] = 1.2
    # below parameter is only applicable for frequency sweep analysis - in optimization S11 is swept
    CM_passive_mixer['simulation']['freq_step'] = 0
    CM_passive_mixer['simulation']['freq_points'] = 3
    CM_passive_mixer['simulation']['loss_iip3'] = False
    # choice of section can be tt_lib or any of the fast slow corners ("for process corner variations")
    CM_passive_mixer['simulation']['section'] = "tt_lib"

    S11_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_S11.scs"

    gain_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_gain.scs"
    
    NF_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_NF.scs"

    iip3_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_iip3.scs"
    
    pss_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_pss.scs"

    # relevant netlists for simulation in opt is stored in the below dict
    CM_passive_mixer['simulation']['netlists'] = {}
    CM_passive_mixer['simulation']['netlists']['S11_netlist'] = S11_netlist
   
    CM_passive_mixer['simulation']['netlists']['gain_netlist'] = gain_netlist
    
    CM_passive_mixer['simulation']['netlists']['NF_netlist'] = NF_netlist

    CM_passive_mixer['simulation']['netlists']['iip3_netlist'] = iip3_netlist

    CM_passive_mixer['simulation']['netlists']['pss_netlist'] = pss_netlist

    # simulation details specific to iip3
    CM_passive_mixer['simulation']['iip3'] = {
        # tone 1 and tone 2 here are with respect to flo
        'tone 1':1e6,
        'tone 2':1.1e6,
        'prf':-10,
        'prf_min':-10,
        'prf_max':15,
        'prf_step':1,
        'ocean_script':{
            'write_ip3_slope_to_CSV_path':"/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/write_ip3_slope_to_CSV.ocn",
            'extract_iip3_post_optimization_path':"/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_iip3_post_optimization.ocn"
        }
    }
 
    # for simulations the dictionary contains the ocean script file path for extracting outputs
    CM_passive_mixer['simulation']['S11'] = {}
    CM_passive_mixer['simulation']['S11']['ocean_script'] = "/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_s11.ocn"
    CM_passive_mixer['simulation']['extract_results'] = {}
    CM_passive_mixer['simulation']['extract_results']['ocean_script'] = "/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_VM/extract_results.ocn"

# END of get_simulation_conditions()

def get_optimization_parameters(CM_passive_mixer):
    CM_passive_mixer['optimization'] = {
        'loss_weights':{
            'S11_db':{},
            'gain_db':{},
            'NF_db':{},
            'iip3':{},
            'Idd':{}
        },
        'max_iteration':300,
        'iter_number':0,
        'delta_threshold':0.001,
        'consec_iter':25,
        # learning rates
        'alpha':{
            'alpha_min':-1,
            'start':0.01,
            'end':0.001,
            'alpha_mult':1,
            'type':'' # type can be linear or log (nothing signifies default of constant alpha)
        },

        'optimizing_variables':['res_w', 'cap_w', 'switch_w', 'rho']

    }
# END of get_optimization_parameters()

# Define a function that sets the simulation parameters for running post optimization simulations
def get_post_optimization_simulation_parameters(CM_passive_mixer):
    # newchange
    # The options in post_optimization are various Analysis to run
    # Analysis types:
    #   1) Frequency analysis - for a given flo, simulate, requested outputs out of gain, NF, S11 and iip3
    #   2) Temperature analysis - simulate the requested outputs out of gain, NF, S11 and iip3 for the given list of temperatures
    #   3) Sentivity - given the delta (% difference) between both arms (LO and LO_bar) of the mixer, simulate the requested outputs
    #   4) Process corners
    # defining the name of netlists files for simulating the output parameters
    # edit netlists in the lines below and uncomment the required lines
    CM_passive_mixer['post_optimization'] = {}
    # details for freq_analysis (all same as temp_analysis - just a single temperature is used)
    CM_passive_mixer['post_optimization']['temp_analysis'] = {}
    CM_passive_mixer['post_optimization']['process_corners'] = {}
    # defining netlists for all simulations
    S11_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_S11.scs"

    gain_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_gain.scs"
    
    NF_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_NF.scs"

    iip3_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_iip3.scs"

    pss_netlist = "/home/ee20b087/cadence_project/BTP_EE20B087/Netlists/CM_pss.scs"

    # details for temperature analysis
    CM_passive_mixer['post_optimization']['temp_analysis']['temp'] = [27, 57]   # temperature list for analysis
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation'] = {}
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['netlists'] = {}
    # setting up the netlists
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['netlists']['S11_netlist'] = S11_netlist
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['netlists']['gain_netlist'] = gain_netlist
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['netlists']['NF_netlist'] = NF_netlist
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['netlists']['iip3_netlist'] = iip3_netlist
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['netlists']['pss_netlist'] = pss_netlist
    # setting flo for which this analysis has to be done
    CM_passive_mixer['post_optimization']['temp_analysis']['flo'] = 500e6
    CM_passive_mixer['post_optimization']['temp_analysis']['RF_Bandwidth'] = CM_passive_mixer['output_conditions']['RF_Bandwidth']
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['temp'] = 27 # this must be replaced with temp from list
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['section'] = "tt_lib"
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['freq_step'] = 10e3
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['iip3'] = {
        # tone 1 and tone 2 here are with respect to flo
        'tone 1':1e6,
        'tone 2':1.1e6,
        'prf':-10,
        'prf_min':-30,
        'prf_max':-10,
        'prf_step':1,
        'ocean_script':{
            'write_ip3_slope_to_CSV_path':"/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/write_ip3_slope_to_CSV.ocn",
            'extract_iip3_post_optimization_path':"/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_iip3_post_optimization.ocn"
        }
    }
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['S11'] = {}
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['S11']['.out_file_path'] = "/home/ee20b087/cadence_project/BTP_EE20B087/sp_sweep.out"
    # for gain key in the dictionary contains the ocean script file path
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['gain'] = {}
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['gain']['ocean_script'] = "/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_sweep_gain.ocn"
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['NF'] = {}
    CM_passive_mixer['post_optimization']['temp_analysis']['simulation']['NF']['ocean_script'] = "/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_NF.ocn"

    # details for process corners analysis
    CM_passive_mixer['post_optimization']['process_corners']['section'] = ["ff_lib", "ss_lib"]   # list of sections needed to be analysed
    CM_passive_mixer['post_optimization']['process_corners']['simulation'] = {}
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['netlists'] = {}
    # setting up the netlists
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['netlists']['S11_netlist'] = S11_netlist
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['netlists']['gain_netlist'] = gain_netlist
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['netlists']['NF_netlist'] = NF_netlist
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['netlists']['iip3_netlist'] = iip3_netlist
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['netlists']['pss_netlist'] = pss_netlist
    # setting flo for which this analysis has to be done
    CM_passive_mixer['post_optimization']['process_corners']['flo'] = 500e6
    CM_passive_mixer['post_optimization']['process_corners']['RF_Bandwidth'] = CM_passive_mixer['output_conditions']['RF_Bandwidth']
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['temp'] = 27
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['section'] = "ff_lib" # this must be replaced with the required section from the list above
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['freq_step'] = 10e3
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['iip3'] = {
        # tone 1 and tone 2 here are with respect to flo
        'tone 1':1e6,
        'tone 2':1.1e6,
        'prf':-10,
        'prf_min':-30,
        'prf_max':-10,
        'prf_step':1,
        'ocean_script':{
            'write_ip3_slope_to_CSV_path':"/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/write_ip3_slope_to_CSV.ocn",
            'extract_iip3_post_optimization_path':"/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_iip3_post_optimization.ocn"
        }
    }
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['S11'] = {}
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['S11']['.out_file_path'] = "/home/ee20b087/cadence_project/BTP_EE20B087/sp_sweep.out"
    # for gain key in the dictionary contains the ocean script file path
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['gain'] = {}
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['gain']['ocean_script'] = "/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_sweep_gain.ocn"
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['NF'] = {}
    CM_passive_mixer['post_optimization']['process_corners']['simulation']['NF']['ocean_script'] = "/home/ee20b087/cadence_project/BTP_EE20B087/Passive_Mixer_CM/extract_NF.ocn"

# END of get_post_optimization_simulation_parameters()

def get_hand_calculated_circuit_parameters(CM_passive_mixer):
    CM_passive_mixer['hand_calculated_circuit_parameters'] = {}
    cm_hc.hand_calculation(CM_passive_mixer['output_conditions'],CM_passive_mixer['hand_calculated_circuit_parameters'])
# END of get_hand_calculated_circuit_parameters()

def set_loss_weights(CM_passive_mixer):
    # for S11 loss_weights we require min_LO_freq, max_LO_freq and freq points to create the flo array
    # after flo_array creation, S11 loss weights are set for each flo in array 
    f_min = CM_passive_mixer['output_conditions']['min_LO_freq']
    f_max = CM_passive_mixer['output_conditions']['max_LO_freq']
    freq_points = CM_passive_mixer['simulation']['freq_points']
    flo_array = np.linspace(f_min, f_max, freq_points)
    # setting a constant S11,gain weight for all flo frequencies

    S11_loss_weight = 0.05
    gain_loss_weight = 0.1
    NF_loss_weight = 0.1
    iip3_loss_weight = 0.1
    Idd_loss_weight = 0.1
    # if weight changes with flo, then accordingly the S11_loss_weight/gain_loss_weight must be defined as an array/dict 
    for flo in flo_array:
        CM_passive_mixer['optimization']['loss_weights']['S11_db'][flo] = S11_loss_weight
        CM_passive_mixer['optimization']['loss_weights']['gain_db'][flo] = gain_loss_weight
        CM_passive_mixer['optimization']['loss_weights']['NF_db'][flo] = NF_loss_weight
        CM_passive_mixer['optimization']['loss_weights']['iip3'][flo] = iip3_loss_weight
        CM_passive_mixer['optimization']['loss_weights']['Idd'][flo] = Idd_loss_weight
    # END of for
# END of set_loss_weights()
"""
===========================================================================================================================
------------------------------------------------- MAIN PROGRAM ------------------------------------------------------------
"""
# defining a master dict that contains all the details related to the Voltage mode passive mixer circuit
CM_passive_mixer = {}
# setting the output conditions
get_output_conditions(CM_passive_mixer)
# setting the simulation conditions
get_simulation_conditions(CM_passive_mixer)
# setting the optimization parameters
get_optimization_parameters(CM_passive_mixer)
# newchange
# getting the post optimization simulation parameters
get_post_optimization_simulation_parameters(CM_passive_mixer)
# end newchange
# based on the output_conditions dict, we find the hand_calculated_circuit_parameters
get_hand_calculated_circuit_parameters(CM_passive_mixer)
# now that all the required settings are initialized, we set the loss weights
set_loss_weights(CM_passive_mixer)
# ---------------------- Creating class 'Circuit' object for CM_passive_mixer -------------------------
cir = gd.Circuit(CM_passive_mixer['hand_calculated_circuit_parameters'], CM_passive_mixer['simulation'], "CM")
# the circuit object named 'cir' is initialized with initial, pre_iteration_circuit_parameters = hand_calculated_circuit_parameters
# and simulation_parameters = simulation dict of CM_passive_mixer
# ----------------------------- calling the full optimization function --------------------------------

fo.full_opt(cir, CM_passive_mixer['optimization'], CM_passive_mixer['output_conditions'])
# full_opt carries out optimization iterations

# ---------------------------------------- ANALYSIS FUNCTIONS -----------------------------------------
# defining run variables, set them as True or False based on whether you want to run them or not
run_freq_analysis = False
run_temp_analysis = False
run_process_corners = False
# FREQUENCY ANALYSIS
# for freq_analysis we give the same details as in the temp_analysis dict, only difference being that simulation is run at a fixed temperature
if run_freq_analysis == True:
    print("-------------------------------- Running post optimization frequency analysis --------------------------------------\n")
    fa.freq_analysis(cir, CM_passive_mixer['post_optimization']['temp_analysis'])
else:
    print("-------------------------------- Skipping post optimization frequency analysis --------------------------------------\n")
# TEMPERATURE ANALYSIS
if run_temp_analysis == True:
    print("-------------------------------- Running post optimization temperature analysis --------------------------------------\n")
    ta.temperature_analysis(cir, CM_passive_mixer['post_optimization']['temp_analysis'])
else:
    print("-------------------------------- Skipping post optimization temperature analysis --------------------------------------\n")
# PROCESS CORNERS ANALYSIS
if run_process_corners == True:
    print("------------------------------- Running post optimization process corners analysis --------------------------------------\n")
    pc.process_corners_analysis(cir, CM_passive_mixer['post_optimization']['process_corners'])
else:
    print("------------------------------- Skipping post optimization process corners analysis --------------------------------------\n")
