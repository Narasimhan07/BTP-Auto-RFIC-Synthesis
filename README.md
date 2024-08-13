------------------------------------------------------ Automatic RF IC Synthesis -------------------------------------------------------------------
Name: Narasimhan Srikanth
Roll number: EE20B087
----------------------------------------------------------------------------------------------------------------------------------------------------
This README file contains information about all the folders and files present in this workspace
1) Netlists: contains netlists of Voltage mode (VM) and current mode (CM) mixers for various measurements 

2) Passive_Mixer_VM/Passive_Mixer_CM: these folders contain the crux of the gradient descent algorithm
    A) CM_hand_calculation.py computes the initial components values from hand calculated formulas
    B) full optimization.py is called in every iteration of the gradient descent algorithm. It updates the learning parameters, computes the slope and updates circuit component values based on the slope.
    C) gradient_descent.py implements the gradient descent algorithm for each iteration by calculating slope and updating circuit values
    D) once optimization is complete the analysis.py files run the temperature, frequency and corner analysis
    E) common functions.py: contains helper functions to plot data, read outputs from ocean scripts, execute simulations in cadence virtuoso all from python

3) VM_call_optimization_function/CM_call_optimization_function.py: it calls the full_optimization.py file and runs the optimization routine


Supporting files (for test cases, etc.)
1) pytest: contains matplotlib functions which can individually plot data in csv files. Pytest also contains test data in csv files and a test version of the gradient descent algorithm

2) there are some ocean scripts (.ocn files) within this workspace. These are files that will extract the output after cadence simulations and store in it csv or text file formats
