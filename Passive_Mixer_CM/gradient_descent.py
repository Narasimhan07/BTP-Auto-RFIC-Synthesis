# =========================================== GRADIENT DESCENT ALOGORITHM ================================================================
# This file contains the required function definitions to carry out gradient descent for the passive mixer circuit
# 
# Optimizing output parameters -  output differential gain (dB), input impedance (S11), integrated SSB Noise figure, iip3 
#   circuit parameters - resistance width, capacitance width & length, effective width of the switch NMOS = sw_fin*(width per finger)
#   loss function:
#       flo is varied over min_LO_freq to max_LO_freq - number of point is a choice from user
#       S11 and gain are evaluated at flo+Bandwidth at each flo frequency
#       The noise figure and iip3 values depend on the integration over Bandwidth and two tones near the chosen flo respectively
#       loss is calculated using ramp(x)
#       loss wrt each  output parameter = sum over all flo values: ramp(S11@flo - S11_0)
#   Function definitions: (eg. given wrt S11 here)
#       calc_loss() - output_conditions(S11 spec), extracted_parameters(S11[:]), loss_weights(for calculated S11 array[:])
#       calc_loss_slope() - slope wrt optimizing variables - res_W, cap_w and sw_fin; delta to find the slope must be specified
# ----------------------------------------------------------------------------------------------------------------------------------------
import os
import numpy as np
import copy
import Passive_Mixer_CM.common_functions as cf
# ----------------------------------------------------------------------------------------------------------------------------------------
# Contents of each class 'Circuit' object variable
#   1. initial_circuit_parameters/hand_calculated_circuit_parameters/pre_iteration_circuit_parameters/post_iteration_circuit_parameters:
#       dict: {'res_w', 'cap_w', 'sw_fin', 'sw_mul', 'switch_w', 'w_per_fin'}
#   2. simulation_parameters: 
#       {'temp', 'freq_points', 'netlists'{ contains the path for various netlists used in opt }, '.out_file_path'{ contains .out fle path for different simulations needed for opt}}
#   3. simulated_output_parameters: (more outputs to be added)
#       {S11_db{ simulated s11 parameters at different flo frequencies }}
# ----------------------------- Creating a class for circuit --------------------------------
class Circuit:
    # --------------------------- Initialization function -----------------------------------
    def __init__(self, circuit_initialization_parameters, initial_simulation_parameters, circuit_type):  
        # circuit_initialization_parameters will be VM_passive_mixer[hand_calculated_circuit_parameters]
        # initial_simulation_parameters will be VM_passive_mixer[simulation]
        # circuit_type will be VM - voltage mode or CM - current mode

        self.initial_circuit_parameters = {}
        self.simulation_parameters = {}
        self.pre_iteration_circuit_parameters = {}
        self.post_iteration_circuit_parameters = {}
        # setting item named type in the class to the type of circuit
        self.type = circuit_type
        # defining a new dict that stored the circuit parameters after optimization
        self.post_optimization_circuit_parameters = {}
        # simulated output parameters stores the output simulation results afer each iteration
        self.simulated_output_parameters = {}
        # creating an empty dict to store S11 parameters from single pt simulation
        self.simulated_output_parameters['S11_db'] = {}
        self.simulated_output_parameters['gain_db'] = {}
        self.simulated_output_parameters['NF_db'] = {}
        self.simulated_output_parameters['iip3'] = {}
        self.simulated_output_parameters['Idd'] = {}
        # Copying the hand calculated values into the initial circuit parameters
        self.initial_circuit_parameters = copy.deepcopy(circuit_initialization_parameters)

        # Copying the initial simulation settings into the simulation parameters
        self.simulation_parameters = copy.deepcopy(initial_simulation_parameters)

        # for the first iteration (iter #1) the pre_iteration_circuit_parameters are same as the hand calculated circuit parameters
        self.pre_iteration_circuit_parameters = copy.deepcopy(circuit_initialization_parameters)

    # END OF __init__()

    # --------------------------- Loss function ---------------------------------------------
    def calc_loss(self, loss_weights, output_conditions):
        # simulated output parameters extracted from spectre
        # S11 is a dictionary of elements of the formats [flo]:[S11_db] where flo goes from min_LO_freq to max_LO_freq
        # loss_weights is an dictionary with the set of keys as S11
        S11 = copy.deepcopy(self.simulated_output_parameters['S11_db'])
        gain = copy.deepcopy(self.simulated_output_parameters['gain_db'])
        NF = copy.deepcopy(self.simulated_output_parameters['NF_db'])
        iip3 = copy.deepcopy(self.simulated_output_parameters['iip3'])
        Idd = copy.deepcopy(self.simulated_output_parameters['Idd'])

        # reference specification
        S11_ref = output_conditions['S11_db']
        gain_ref = output_conditions['gain_db']
        NF_ref = output_conditions['NF_db']
        iip3_ref = output_conditions['iip3']
        # for Idd the reference is zero because we want to minimise current consumption

        # define Loss variables for each output simulated parameters as 0
        loss_S11 = 0
        loss_gain = 0
        loss_NF = 0
        loss_iip3 = 0
        loss_Idd = 0
        
        for flo in S11:
            # defining two different loss functions based on the circuit type for loss_S11
            if self.type == "VM":
                loss_S11 = loss_S11 + loss_weights['S11_db'][flo]*cf.ramp_func(S11[flo] - S11_ref)
            elif self.type == "CM":
                loss_S11 = loss_S11 + loss_weights['S11_db'][flo]*cf.ramp_func(S11[flo] - S11_ref)
            # loss functions for gain, NF and iip3 are same for both VM and CM
            loss_gain = loss_gain + loss_weights['gain_db'][flo]*cf.ramp_func(gain_ref - gain[flo])
            loss_NF = loss_NF + loss_weights['NF_db'][flo]*cf.ramp_func(NF[flo] - NF_ref)
            loss_iip3 = loss_iip3 + loss_weights['iip3'][flo]*cf.ramp_func(iip3_ref - iip3[flo])
            loss_Idd = loss_Idd + loss_weights['Idd'][flo]*Idd[flo]

        # defining total loss as the sum of all losses
        loss = loss_S11 + loss_gain + loss_NF + loss_iip3 + loss_Idd
        
        # defining a loss_dict that returns the individual losses and total loss
        loss_dict = {
            'loss':loss,
            'loss_S11':loss_S11,
            'loss_gain':loss_gain,
            'loss_NF':loss_NF,
            'loss_iip3':loss_iip3,
            'loss_Idd':loss_Idd
        }
        return loss_dict
    
    # END OF calc_loss()

    # -------------------------- Function to run the circuit and return extracted parameters -----------------------
    def run_circuit(self, output_conditions):

        # simulation parameters contain the required simulation details that need to be included in the circuit
        # The pre_iteration_circuit_parameters are used to edit the netlist file
        # for each simulation: flo is varied from min_LO_freq to max_LO_freq with total number of points = freq_points
        freq_points = self.simulation_parameters['freq_points']
        # defining an array for flo 
        flo_array = np.linspace(output_conditions['min_LO_freq'], output_conditions['max_LO_freq'],freq_points)

        # 1) simulate the s11 netlist and extract s11 information
        # edit S11 netlist with global and s11 netlist edit functions
        cf.global_netlist_edit(self.simulation_parameters['netlists']['S11_netlist'], flo_array, output_conditions['RF_Bandwidth'],
        self.pre_iteration_circuit_parameters, self.simulation_parameters
        )
        cf.S11_netlist_edit(self.simulation_parameters, "single_point")
        cf.run_spectre_with_PSF_file(self.simulation_parameters['netlists']['S11_netlist'])
        # extracting the s11 values after simulation
        freq_list, S11_db_list = cf.extract_S11(self.simulation_parameters['S11']['ocean_script'])
        i = 0
        for flo in freq_list:
            # a) adding s11 results
            self.simulated_output_parameters['S11_db'][flo] = S11_db_list[i]
            i = i + 1

        # 2) running pss sweep followed by pac and pnoise simulation for the frequency points
        cf.global_netlist_edit(self.simulation_parameters['netlists']['pss_netlist'], flo_array, output_conditions['RF_Bandwidth'],
        self.pre_iteration_circuit_parameters, self.simulation_parameters
        )
        # edit the pac statement inside this netlist
        cf.gain_netlist_edit(self.simulation_parameters, "single_point")
        # run the simulation for pac and pnoise
        cf.run_spectre_with_PSF_file(self.simulation_parameters['netlists']['pss_netlist'])
        # extracting the noise and gain results
        freq_list, gain_db_list, NF_db_list, idd_list = cf.extract_results(self.simulation_parameters['extract_results']['ocean_script'])
        i = 0
        for flo in freq_list:
            # a) adding gain results
            self.simulated_output_parameters['gain_db'][flo] = gain_db_list[i]
            # b) adding NF results
            self.simulated_output_parameters['NF_db'][flo] = NF_db_list[i]
            # c) adding idd results
            self.simulated_output_parameters['Idd'][flo] = idd_list[i]
            i = i + 1

        # 3) Adding iip3 results at LO = flo to the simulated output parameters dict
        for flo in flo_array:
            if self.simulation_parameters['loss_iip3'] == True:
            # Edit the iip3 netlist with the circuit parameters
                cf.iip3_netlist_edit(
                    flo, self.pre_iteration_circuit_parameters, self.simulation_parameters
                )
                # simulate the spectre netlist for gain and the respective psf file with outputs
                cf.run_spectre_with_PSF_file(self.simulation_parameters['netlists']['iip3_netlist'])
                
                # iip3 computed at flo is stored in the dict in simulated output parameters using the key = flo
                self.simulated_output_parameters['iip3'][flo] = cf.extract_iip3(self.simulation_parameters['iip3']['ocean_script'])
            else:
                iip3_const = 5
                self.simulated_output_parameters['iip3'][flo] = output_conditions['iip3'] + iip3_const

        # END for loop

    # END of run_circuit()

    # ------------- Function to run the circuit for multiple circuit parameters and return simulated outputs -----------------------
    def run_circuit_multiple(self, output_conditions, initial_circuit_parameters_dict):

        # simulation parameters contain the required simulation details that need to be included in the circuit
        # The initial_circuit_parameters_dict are used to edit the netlist file
        # for S11 simulation: flo is varied from min_LO_freq to max_LO_freq with total number of points = freq_points
        freq_points = self.simulation_parameters['freq_points']
        # defining an array for flo 
        flo_array = np.linspace(output_conditions['min_LO_freq'], output_conditions['max_LO_freq'],freq_points)
        # define the simulated output parameters dict
        simulated_output_parameters_dict = {}

        for i in initial_circuit_parameters_dict:
            simulated_output_parameters_dict[i] = {
                'S11_db':{},
                'gain_db':{},
                'NF_db':{},
                'iip3':{},
                'Idd':{}
            }
            # 1) simulate the s11 netlist and extract s11 information
            cf.global_netlist_edit(self.simulation_parameters['netlists']['S11_netlist'], flo_array, output_conditions['RF_Bandwidth'],
            initial_circuit_parameters_dict[i], self.simulation_parameters
            )
            cf.S11_netlist_edit(self.simulation_parameters, "single_point")
            cf.run_spectre_with_PSF_file(self.simulation_parameters['netlists']['S11_netlist'])
            # extracting the s11 values after simulation
            freq_list, S11_db_list = cf.extract_S11(self.simulation_parameters['S11']['ocean_script'])
            j = 0
            for flo in freq_list:
                # a) adding s11 results
                simulated_output_parameters_dict[i]['S11_db'][flo] = S11_db_list[j]
                j = j + 1
            
            # 2) running pss sweep followed by pac and pnoise simulation for the frequency points
            cf.global_netlist_edit(self.simulation_parameters['netlists']['pss_netlist'], flo_array, output_conditions['RF_Bandwidth'],
            initial_circuit_parameters_dict[i], self.simulation_parameters
            )
            # edit the pac statement inside this netlist
            cf.gain_netlist_edit(self.simulation_parameters, "single_point")
            # run the simulation for pac and pnoise
            cf.run_spectre_with_PSF_file(self.simulation_parameters['netlists']['pss_netlist'])
            # extracting the noise and gain results
            freq_list, gain_db_list, NF_db_list, idd_list = cf.extract_results(self.simulation_parameters['extract_results']['ocean_script'])
            j = 0
            for flo in freq_list:
                # a) adding gain results
                simulated_output_parameters_dict[i]['gain_db'][flo] = gain_db_list[j]
                # b) adding NF results
                simulated_output_parameters_dict[i]['NF_db'][flo] = NF_db_list[j]
                # c) adding idd results
                simulated_output_parameters_dict[i]['Idd'][flo] = idd_list[j]
                j = j + 1
            
            # 3) Adding iip3 results at LO = flo to the simulated output parameters dict
            for flo in flo_array:
                if self.simulation_parameters['loss_iip3'] == True:
                # Edit the iip3 netlist with the circuit parameters
                    cf.iip3_netlist_edit(
                        flo, initial_circuit_parameters_dict[i], self.simulation_parameters
                    )
                    # simulate the spectre netlist
                    cf.run_spectre_with_PSF_file(self.simulation_parameters['netlists']['iip3_netlist'])
                    # read the output from ocean scripts
                    # iip3 computed at flo is stored in the dict in simulated output parameters using the key = flo
                    simulated_output_parameters_dict[i]['iip3'][flo] = cf.extract_iip3(self.simulation_parameters['iip3']['ocean_script'])
                else:
                    iip3_const = 5
                    simulated_output_parameters_dict[i]['iip3'][flo] = output_conditions['iip3'] + iip3_const

            # END for loop
            # END of obtaining simulated output parameters for one set of initial circuit parameters in initial_circuit_parameters_dict
        # END for loop
        return simulated_output_parameters_dict

    # END of run_circuit_multiple()

    # ----------------- Updating circuit parameters --------------------------------
    def update_circuit_parameters(self, circuit_parameters_slope, optimization_parameters, loss_iter, alpha):
        # getting the names of loss parameters that must be considered for circuit updation
        flag_zero_loss = 0
        # if all the params in loss_iter become 0 then fag_zero_loss is set to one and iterations are stopped
        change_loss_parameters = []
        for param in loss_iter:
            if param == 'loss':
                continue
            if loss_iter[param] == 0:
                continue
            # Those loss parameters that are not zero only will be considered for updating circuit parameter
            change_loss_parameters.append(param)
        # END for loop
        # alpha = learning rate for the given iteration

        self.post_iteration_circuit_parameters = self.get_pre_iteration_circuit_parameters()
        if change_loss_parameters == []:
            flag_zero_loss = 1
            return flag_zero_loss
        else:
            # now using the slope, we calculate the update of each circuit parameter
            for parameter in circuit_parameters_slope:
                change = 0
                for loss_name in change_loss_parameters:
                    change  = change + circuit_parameters_slope[parameter][loss_name]
                # END for loop
                # increment = slope*learning rate*(pre_iteration_circuit_parameter)^2
                change = change*alpha*(self.pre_iteration_circuit_parameters[parameter]**2)
                # now we check if this change is more than 25% of the parameter value
                # if YES, we limit the change to 25% only
                change_limit = 0.25
                if(change > change_limit*self.pre_iteration_circuit_parameters[parameter]):
                    change = change_limit*self.pre_iteration_circuit_parameters[parameter]
                if(change < (-1)*change_limit*self.pre_iteration_circuit_parameters[parameter]):
                    change = (-1)*change_limit*self.pre_iteration_circuit_parameters[parameter]
                # ENTER THE UPDATING PARAMETER EQUATIONS
                if parameter == 'switch_w':
                    # first we increment or decrement the switch_w based on slope of the loss function
                    self.post_iteration_circuit_parameters[parameter] = self.post_iteration_circuit_parameters[parameter] - change
                    # we round of this switch_w to get the updated value of sw_mul
                    self.post_iteration_circuit_parameters['sw_mul'] = float(int(self.post_iteration_circuit_parameters[parameter]*1e6))
                    # we get the updated sw_wn by dividing the switch_w by the updated sw_mul
                    self.post_iteration_circuit_parameters['sw_wn'] = self.get_post_iteration_circuit_parameters[parameter]/self.post_iteration_circuit_parameters['sw_mul']
                elif parameter == 'rho':
                    # first we remove the keys related to buffer except rho in the post_iteration_optimisation_parameters
                    remove_keys = []
                    for key in self.post_iteration_circuit_parameters:
                        if key == 'res_w' or key == 'cap_w' or key == 'switch_w' or key == 'sw_wn' or key == 'sw_mul' or key == 'rho' or key == 'G' or key == 'RN' or key == 'gm':
                            continue
                        else:
                            remove_keys.append(key)
                    for key in remove_keys:
                        del self.post_iteration_circuit_parameters[key]

                    # first we increment or decrement the rho value based on the slope of the loss function
                    self.post_iteration_circuit_parameters[parameter] = self.post_iteration_circuit_parameters[parameter] - change
                    # finding the new values of the buffer block parameters based on rho
                    load_cap = self.post_iteration_circuit_parameters['switch_w']*(1e-15/1e-6)
                    N, wp_total, wn_total, wp, wn, mp, mn = cf.buffer_block(self.post_iteration_circuit_parameters[parameter], load_cap)
                    self.post_iteration_circuit_parameters['N'] = N
                    i=0
                    while i < N:
                        str1 = "wp" + str(i) + "_total"
                        str2 = "wn" + str(i) + "_total"
                        str3 = "wp" + str(i) 
                        str4 = "wn" + str(i)
                        str5 = "mp" + str(i)
                        str6 = "mn" + str(i)
                        self.post_iteration_circuit_parameters[str1] = wp_total[i]
                        self.post_iteration_circuit_parameters[str2] = wn_total[i]
                        self.post_iteration_circuit_parameters[str3] = wp[i]
                        self.post_iteration_circuit_parameters[str4] = wn[i]
                        self.post_iteration_circuit_parameters[str5] = mp[i]
                        self.post_iteration_circuit_parameters[str6] = mn[i]
                        i = i + 1

                else:
                    self.post_iteration_circuit_parameters[parameter] = self.post_iteration_circuit_parameters[parameter] - change
            # END for loop
            # new set of pre_iteration circuit parameters are now transfered from the post interation parameters dict
            self.pre_iteration_circuit_parameters = self.get_post_iteration_circuit_parameters()

            # updating the iteration number
            optimization_parameters['iter_number'] += 1
            return flag_zero_loss
        # END else block
    
    # END of update_circuit_parameters()

    # ----------------- Getting the pre iter circuit parameters --------------------
    def get_pre_iteration_circuit_parameters(self):
        return self.pre_iteration_circuit_parameters.copy()
    # END of get_pre_iteration_circuit_parameters()

    # ----------------- Getting the post iter circuit parameters --------------------
    def get_post_iteration_circuit_parameters(self):
        return self.post_iteration_circuit_parameters.copy()
    # END of get_post_iteration_circuit_parameters()

    # ----------------- Getting the simulated output parameters --------------------
    def get_simulated_output_parameters(self):
        # we use deepcopy() because it has nested dictionaries
        return copy.deepcopy(self.simulated_output_parameters)
    # END of get_simulated_output_parameter()

# --------------------------- END of class Circuit --------------------------------

# ----------------------- Computing Loss function slope ---------------------------
def calc_loss_slope(cir,output_conditions,loss_dict,optimization_parameters):

    loss_weights = copy.deepcopy(optimization_parameters['loss_weights'])
    # loss_weights is a dict with nested dict for S11_db's weights
    delta_threshold = optimization_parameters['delta_threshold']
	
	# Getting the slope dictionary
    circuit_parameters_slope={} 
    # This dictionary will store the values of slope of different losses with change of all circuit parameters
	
	# Getting initial values stored in a dict
    initial_circuit_parameters = cir.get_pre_iteration_circuit_parameters()
    initial_simulated_output_parameters = cir.get_simulated_output_parameters()

	# Getting the list of circuit and extracted parameters
    initial_circuit_parameters_dict={}
    simulated_output_parameters_dict={}

	# Calculating the initial circuit parameters dict
    i=0
    for param_name in optimization_parameters['optimizing_variables']:
		# Calculating the increment value
        if param_name == 'switch_w':
            increment_factor = delta_threshold
            # The value by which parameter increases = increment_factor*parameter
            increment = initial_circuit_parameters[param_name]*increment_factor
        else:
            increment_factor = delta_threshold
            # The value by which parameter increases = increment_factor*parameter
            increment = initial_circuit_parameters[param_name]*increment_factor

		# Incrementing the circuit parameter
        initial_circuit_parameters_dict[i] = initial_circuit_parameters.copy()
        initial_circuit_parameters_dict[i][param_name] = initial_circuit_parameters_dict[i][param_name] + increment
        # below, we adjust the wn of nmos to get the incremented switch_w and keep the same number of sw_mul
        if param_name == 'switch_w':
            new_wn = initial_circuit_parameters_dict[i][param_name]/float(initial_circuit_parameters_dict[i]['sw_mul'])
            initial_circuit_parameters_dict[i]['sw_wn'] = new_wn
        elif param_name == 'rho':
            load_cap = initial_circuit_parameters_dict[i]['switch_w']*(1e-15/1e-6)
            N, wp_total, wn_total, wp, wn, mp, mn = cf.buffer_block(initial_circuit_parameters_dict[i][param_name], load_cap)
            initial_circuit_parameters_dict[i]['N'] = N
            j=0
            while j < N:
                str1 = "wp" + str(j) + "_total"
                str2 = "wn" + str(j) + "_total"
                str3 = "wp" + str(j) 
                str4 = "wn" + str(j)
                str5 = "mp" + str(j)
                str6 = "mn" + str(j)
                initial_circuit_parameters_dict[i][str1] = wp_total[j]
                initial_circuit_parameters_dict[i][str2] = wn_total[j]
                initial_circuit_parameters_dict[i][str3] = wp[j]
                initial_circuit_parameters_dict[i][str4] = wn[j]
                initial_circuit_parameters_dict[i][str5] = mp[j]
                initial_circuit_parameters_dict[i][str6] = mn[j]
                j = j + 1
        i+=1

    # Each key (denoted by 'i') in initial_circuit_parameters_dict holds the circuit_parameters wherein one of the parameters is incremented
    # wrt to the pre_iteration_circuit_parameters
	# Running the circuits and calculating the loss
    print("----------------------------- Calculating slope optimizing variables ---------------------------------\n")
    simulated_output_parameters_dict = cir.run_circuit_multiple(output_conditions, initial_circuit_parameters_dict)

	# print(simulated_output_parameters_dict)

	# Calculating the slope and sensitivity
    i=0
    for param_name in optimization_parameters['optimizing_variables']:
        # to calculated the new loss function after incrementing a particular optimizing variable
        # first, initialize the simulated output parameters to the dict holding the simulated output parameters for that optimizing variable
        cir.simulated_output_parameters = copy.deepcopy(simulated_output_parameters_dict[i])
        # next, calculate the loss function for these set of simulated output parameters
        loss_dict1 = cir.calc_loss(loss_weights, output_conditions)
        i+=1
		
		# Calculating Slope	
        circuit_parameters_slope[param_name]={}
        # recalling the increment value for the optimizing variable for calculating slope
        if param_name == 'switch_w':
            increment = initial_circuit_parameters[param_name]*increment_factor
        else:
            increment = initial_circuit_parameters[param_name]*increment_factor

        for param in loss_dict:
        	circuit_parameters_slope[param_name][param]=(loss_dict1[param]-loss_dict[param])/increment
		# END of slope calculation for 1 optimizing variable
    # END of circuit_parameters_slope calculation
	
    cir.simulated_output_parameters = initial_simulated_output_parameters.copy()
    print("-------------------------------------- slope calculation complete --------------------------------------------\n")
    return circuit_parameters_slope
# END of circuit_parameters_slope()
# --------------------- Function to update learning rate after each iter -----------------------
def update_alpha(optimization_parameters, iter_number, alpha, alpha_mult):
    max_iteration = optimization_parameters['max_iteration'] - 1
    alpha_start = optimization_parameters['alpha']['start']
    alpha_end = optimization_parameters['alpha']['end']

    if optimization_parameters['alpha']['type']=='linear':
    	alpha = alpha_start + (((alpha_end - alpha_start)*(iter_number - 1))/max_iteration)

    elif optimization_parameters['alpha']['type']=='log':
	    alpha_start_log = np.log(alpha_start)
	    alpha_end_log = np.log(alpha_end)
	    alpha_log = alpha_start_log + ((alpha_end_log - alpha_start_log)*(iter_number - 1)/max_iteration)
	    alpha = np.exp(alpha_log)
		
    else:
        # alpha is constant
        alpha = alpha*alpha_mult
		
    return alpha
# END of update_alpha()

# ---------------------------------- stop functions ------------------------------------------
# Checking stopping condition ( if loss increases for n_iter consecutive number of iterations )
def check_stop_loss(loss_iter,iter_number,n_iter):

	flag=0
	if n_iter<1:
		return 0
	if iter_number>n_iter:
		flag=1
		for j in range(n_iter):
			if loss_iter[iter_number-j]['loss']<loss_iter[iter_number-j-1]['loss']:
				flag=0

	return flag
# END of check_stop_loss()

# Checking stopping condition ( if alpha<alpha_min )
def check_stop_alpha(alpha,iter_number,alpha_min):

	if alpha_min<0:
		return 0
	if iter_number>1:
		if alpha<=alpha_min:
			return 1
	return 0
# END of check_stop_alpha()
