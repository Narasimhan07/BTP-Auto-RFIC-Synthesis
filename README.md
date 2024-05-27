Analysing BTP code
(A) Main_optimization_CG_LNA.py
    Variables:
        circuit_initialization_parameters - {
            {mos_parameters - Vdd, Lmin, un, tox, Cox..},
            {simulation-
                {standard_parameters - directory, temp, iip3 related parameters}, 
                {other netlist related parameters - fund1, fund2, temp, n_harms..}
            }
        }
        optimization_input_parameters - {
            {output_conditions-output specs like gain, s11, iip3..},
            {pre_optimization_parameters - threshold values of components, manual hand calculated values..},
            {optimization_parameters - type of loss, learning rate, number of iterations, loss weights..},
            {sensitivity_analysis_parameters},
            {temperature_analysis_parameters},
            {process_analysis_parameters},
            {frequency_analysis_parameters},
            {iip3_analysis_parameters}
            }
    Functions:
        get_mos_parameters - using process_name to set up mos parameters (not needed for our code)
        get_output_conditions - sets up the output specs needed
        get_simulation_conditions - sets up the simulation variables in circuit_initialization_parameters
        get_pre_optimization_parameters - sets the hand calculated parameters in optimization_input_parameters
        get_optimization_parameters - sets the optimization related parameters
        get_sensitivity_analysis_parameters - sets the parameters need to run sensitivity analysis
        get_temperature_analysis_parameters - sets the parameters need to run temperature analysis
        get_process_analysis_parameters - sets the parameters need to run process analysis
        get_frequency_analysis_parameters - sets the parameters need to run frequency analysis
        get_iip3_analysis_parameters - sets the parameters need to run iip3 analysis
        get_circuit_parameter_analysis_parameters
        complete_optimization - takes optimization_input_parameters and circuit_initialization_parameters to run the optimization function

(B) spectre.py
    Variables
        Class Circuit - object defined by "def __init__(self,circuit_initialization_parameters)"
            attributes - {
                initial_circuit_initialization_parameters,
                circuit_initialization_parameters, 
                initial_circuit_parameters,
                circuit_parameters,
                extracted_parameters,
                mos_parameters
            }
    Functions
        Class circuit:
            __init__ - sets up circuit_initialization_parameters and mos_parameters by using copy.deepcopy() for initial_circuit_initialization_parameters

            Circuit Parameter functions:
                run_circuit - sets circuit_parameters using get_final_circuit_parameters(); sets extracted_parameters using write_extract()
                run_circuit_multiple - sets up extracted_parameters_dict for multiple sets of circuit_parameters in another dict
                update_circuit - updating circuit_parameters and then run_circuit again to get extracted_parameters
                update_circuit_parameters_1 - updating the circuit_parameters using get_final_circuit_parameters() but not running the circuit
                get_initial_circuit_parameters - return a copy() of initial_circuit_parameters
                get_circuit_parameters - return a copy() of circuit_parameters
                get_extracted_parameters - return a copy() of extracted_parameters
                update_circuit_state - updates the initial_circuit_parameters, circuit_parameters and extracted_circuit_parameters
            Simulation Parameter Functions:
                update_simulation_parameters - updates the [simulation][standard_parameters] in circuit_initialization_parameters based on the given simulation_parameters in the function input
                update_temp - updates temperature to the input value in [simulation][netlist_parameters] of circuit_initialization_parameters
                reset_temp - resets temperature to the standard value in [simulation][netlist_parameters] of circuit_initialization_parameters
            Optimization functions:
                calc_loss - takes the extracted_parameters, reference parameters (from ouptut_conditions) and loss_weights
                    loss_wrt_ref_parameter = loss_weight*ramp(extracted_parameter-reference)
                    loss = sum of all the losses wrt all parameters
                    returns individual losses and total loss as a dict
                
Voltage Mode Passive Mixer:
(A) main program:
    Inputs from the user:
        1. RF signal Bandwidth - RF_Bandwidth
        2. LO frequency range - {min_LO_freq, max_LO_freq}
        3. minimum gain over RF Bandwidth - gain
        4. maximum S11 over RF Bandwidth - S11
        5. maximum noise figure over RF Bandwidth - NF
        6. maximum power consumption of the circuit - Power
        7. circuit temp - temp
        
MY BTP CODE - changes to be added
1. Now that we are allowing the width of the nmos switch to change, we must edit the netlist accordingly to make switch width also as a parameter - done✅
2. Adding other simulated output parameters to the loss function - NF, gain, iip3 - done✅
3. Adding the inverter path to the LO inputs - we have to edit the schematic, take in the required parameters
4. adding tsmc components to resistors and capacitors - done✅
5. Analysis code - temperature, sensitivity, process variations, frequency, feedthrough - done✅