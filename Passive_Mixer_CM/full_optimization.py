# =========================================== FULL OPTIMIZATION ================================================================
# This file contains the optimization code that makes use of all the gradient descent functions and  
# class functions of class 'Circuit' to run the optimization run for the circuit
import numpy as np
import copy
import common_functions as cf
import gradient_descent as gd

def full_opt(cir, optimization_parameters, output_conditions):
    # 'cir' is an object of class 'Circuit' which contains the initial_circuit_parameters (which are the hand calculated values),
    # the simulation_parameters and the post_optimization_circuit_parameters.
    # It also contains the functions to run spectre and update circuit parameters
    # All the details pertaining to each iteration will be stored in the dictionaries of the Class object 'cir'

    # let the iteration number be denoted by 'i'
    i = 1
    # defining all the required optimization related variables
    loss_weights = copy.deepcopy(optimization_parameters['loss_weights'])
    alpha_min = optimization_parameters['alpha']['alpha_min']
    alpha_mult = optimization_parameters['alpha']['alpha_mult']
    max_iteration = optimization_parameters['max_iteration']
    # consec_iter is used in the check_stop_loss(): if loss keeps increasing for consec_iter number of iterations
    consec_iter = optimization_parameters['consec_iter']
    alpha_type = optimization_parameters['alpha']['type']
    # based on alpha type we will initialize values of alpha start, alpha end and alpha itself
    if alpha_type == 'linear' or alpha_type == 'log':
        alpha_start = optimization_parameters['alpha']['start']
        alpha_end = optimization_parameters['alpha']['end']
    alpha = optimization_parameters['alpha']['start']
    # Creating the dictionaries
    loss_iter={}
    # This dictionary will store the value of all loss values for different iterations 				
    loss_slope_iter={} 			
    # This dictionary will store the value of slope of losses for all parameters for different iterations
    alpha_parameters_iter={} 		
    # This dictionary will store the value of threshold for different iterations
    simulated_output_parameters_iter={}		
    # This dictionary will store the value of output parameters for different iterations
    post_iteration_circuit_parameters_iter={} 	
    # This dictionary will store the value of circuit parameters for different iterations
    # ------------------------- performing iterations -----------------------------------
    while i<=max_iteration:
        cir.run_circuit(output_conditions)
        # The above will run the circuit and set the simulated output parameters
        simulated_output_parameters_iter[i] = cir.get_simulated_output_parameters()
        # after obtaining simulated output parameters, loss function is calculated
        loss_iter[i] = cir.calc_loss(loss_weights, output_conditions)
        # printing loss for each iteration here
        # using the loss_iter values, we can obtain the loss slope wrt the optimizing variables 
        # optimizing variables are already defined under VM_passive_mixer['optimization']['optimizing_variables']

        print("---------------------------------- Calculating slope for iter = ", i, " --------------------------------------")

        circuit_parameters_slope = gd.calc_loss_slope(cir, output_conditions, loss_iter[i], optimization_parameters)
        loss_slope_iter[i] = copy.deepcopy(circuit_parameters_slope)
        # The circuit parameters are updated using the update circuit function
        alpha_parameters_iter[i] = alpha
        flag_zero_loss = cir.update_circuit_parameters(circuit_parameters_slope, optimization_parameters, loss_iter[i], alpha)
        post_iteration_circuit_parameters_iter[i] = cir.get_post_iteration_circuit_parameters()

        # cf.print_post_iteration(loss_iter, post_iteration_circuit_parameters_iter, i, 2)
        cf.write_opt_results(loss_iter[i],post_iteration_circuit_parameters_iter[i], alpha, i)
        # checks for stop before max_iterations
        flag_loss = gd.check_stop_loss(loss_iter, i, consec_iter)
        flag_apha = gd.check_stop_alpha(alpha, i, alpha_min)
        # iteration number ('i') is incremented to the next value for the next iteration
        i += 1
        # alpha must be updated to the value for the next iteration
        alpha = gd.update_alpha(optimization_parameters, i, alpha, alpha_mult)
        if flag_apha == 1 or flag_loss == 1 or flag_zero_loss == 1:
            break
    # END of iteration loop
    # when we come out of the above loop, post_iteration_circuit_parameters have changed but have not been stored
    cir.run_circuit(output_conditions)
    simulated_output_parameters_iter[i] = cir.get_simulated_output_parameters()
    loss_iter[i] = cir.calc_loss(loss_weights, output_conditions)
    # loss_slope for this value of 'i' will come into use if we continue descent further
    loss_slope_iter[i] = copy.deepcopy(circuit_parameters_slope)
    # saving results from optimization to dict post_optimization_circuit_parameters in 'cir'
    cir.post_optimization_circuit_parameters = cir.get_post_iteration_circuit_parameters()

    print('--------------------------------- optimization results --------------------------------\n')
    print('final_loss: ', loss_iter[i])
    print('Simulated output parameters post optimization: ', simulated_output_parameters_iter[i])
    print('circuit_parameters post optimization: ', cir.post_optimization_circuit_parameters)
    print('----------------------------------- end optimization  ---------------------------------\n')