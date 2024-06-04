# This function updates the values of circuit parameters by trying to minimize loss
def update_circuit_parameters(self,circuit_parameters_slope,optimization_input_parameters,run_number,loss_iter,loss_type):
    
    # Getting the names of loss parameters that should be considered for circuit parameter updation
    change_loss_parameters=[]

    # Loss Type = 0
    if loss_type==0:
        if loss_iter['loss']==loss_iter['loss_Io']:
            change_loss_parameters=['loss_Io']
        else:
            change_loss_parameters=['loss_s11','loss_gain','loss_iip3','loss_nf']
    
    # Loss Type = 1
    elif loss_type==1:
        change_loss_parameters=['loss']

    # Loss Type = 2
    elif loss_type==2:
        for param in loss_iter:
            if param=='loss':
                continue
            if loss_iter[param]==0:
                continue
            change_loss_parameters.append(param)

    
    alpha=optimization_input_parameters['optimization'][run_number]['alpha']['value']

    # Calculating the value to update each parameter with
    for param_name in circuit_parameters_slope:
        
        # Calculating the Increment Value
        change=0
        for loss_name in change_loss_parameters:
            change+=circuit_parameters_slope[param_name][loss_name]
        change=change*(self.initial_circuit_parameters[param_name]**2)*alpha
    
    
        # Checking if the parameter is updated by a large value
        change_limit=0.25 # If the incremented value is more than +- change_limit*parameter_name, then we will limit the change
        if change>change_limit*self.initial_circuit_parameters[param_name]:
            change=change_limit*self.initial_circuit_parameters[param_name]
        if change<-1*change_limit*self.initial_circuit_parameters[param_name]:
            change=-1*change_limit*self.initial_circuit_parameters[param_name]
        
        # Updating circuit_parameters
        self.initial_circuit_parameters[param_name]=self.initial_circuit_parameters[param_name]-change
    
    self.update_circuit_parameters_1(self.initial_circuit_parameters)
        