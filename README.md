# Automatic RF IC Synthesis
## Schematic Design Automation for Passive Downconversion Mixers using Python
###### Narasimhan Srikanth 
###### B.Tech, Department of Electrical Engineering, Indian Institute of Technology Madras

### Motivation behind this Project
Analog design is a tedious task wherein the designer has to go though multiple iterations of fine tuning to arrive at the state-of-the-art specs. It is important to achieve the best design while dissipating as much low power as possible. Standard analog/RF circuit blocks such as amplifiers, mixers, oscillators and buffers take a long time to build and test when it is done manually. With the advent of ***AI*** and ***ML***, automation has become a useful tool in Analog circuit design. Design automation can guide the user by automating layout generation, power minimisation and performance. The optimisation can be completely carried out by the algorithm, saving lots of time and effort spent on it otherwise. 

With a brief motivation about why automation is very important and how it can help circuit design greatly, let us dive straight into this project! 

### A Brief Introduction
In this project, I have worked on the schematic design automation for ***passive downconversion mixers*** operating for a specific LO frequency range. The mixers are of two types; the ***voltage-mode*** mixer and the ***current-mode*** mixer (based on the whether the RF input is a voltage/current). 

***Python*** is the programming language that has been used to carry out schematic design automation. All circuit related simulations are done using ***Cadence Virtuoso***. **SPICE** is the common simulator language used. 

This project's ***final output*** is a **SPICE netlist** describing the desired mixer's design. A few specs that are taken into consideration in autoamation are,
+ voltage conversion gain from RF port to IF port 
+ noise figure
+ input impedance matching and, 
+ minimisation of overall power consumption in the circuit

#### Using Gradient Descent for Automation
In this project, I have used the ***gradient descent*** algorithm to achieve the best set of components suitable for the required specifications and power minimisation. For a brief outline on how the gradient descent algoritm works, [click here](https://realpython.com/gradient-descent-algorithm-python/).

In this project, the ***cost function*** is defined based on the specifications a user would like to keep in mind while designing a passive mixer, like conversion gain, noise figure and impedance matching. 

The automation routine carries out iterations that are otherwise done mannually. The algorithm guides the circuit design towards the most ***optimal solution*** in the neighbourhood. (***Note that*** global optimum is not a guarantee in gradient descent!)

#### How to use this in brief
As a user of this automation program for passive mixer schematic design, you will have to know the type of mixer you wish to designs and the requirements you expect your mixer circuit to meet. 
+ This includes the gain, noise figure, IIP3, input matching that you want you mixer to meet.
+ Based on the requirement the algorithm will choose a starting point for the automation, based on certain hand-derieved formulas/calculations. This may be resistor, capacitor, MOS transistor sizes in the circuit design. This starting point will assume a design skeleton for your mixer and insert hand calculated values to each component in it.
+ Now, the actual automation routine starts optimisation for arriving at the best solution in accordance to your specs.

#### Passive Downconversion Mixers
For more information about passive mixers, their important features, analysis and design considerations you can refer to ***RF Mircroelectronics*** *by* ***Behzad Razavi, Prentice Hall, second edition, 2011***.

To dive deep into input impedance matching in mixer first receiver architectures (direct conversion receivers), you can read the paper by ***C. Andrews and A. C. Molnar***: ***Implications of Passive Mixer Transparency for Impedance Matching and Noise Figure in Passive Mixer-First Receivers***. [*IEEE Transactions on Circuits and Systems I: Regular Papers, 57(12):3092–3103, December 2010*](https://ieeexplore.ieee.org/document/5518350).

All the hand calculations I have done to set up the automation are based on conculsions and concepts from the literature above. 

### Files in this Repository

1. `Netlists`: contains netlists of voltage-mode and current-mode mixers for various measurements. 

2. `Passive_Mixer_VM` and `Passive_Mixer_CM`: these folders contain the crux of the gradient descent algorithm for the mixer design
    + `CM_hand_calculation.py` computes and sets the initial component values before automation from hand-derieved formulas.
    + `full optimization.py` is called in every iteration of the gradient descent algorithm. It updates the circuit component values based on the gradient of the cost function in every iteration.
    + `gradient_descent.py` implements the gradient descent algorithm for each iteration. The key steps involved are,
       + updating cost function at the start of each iteration.
       + calculating gradient w.r.t each circuit component involved in automation.
       + incrementing or decrementing each component as dictated by the gradient in the previous step.
    + once optimization is complete the `name_analysis.py` files run the temperature, frequency and corner analysis.
    + `common functions.py` contains helper functions to plot data, read outputs stored in `.csv`/`.txt` files, execute simulations in cadence virtuoso - all of this from the Python program

3. `VM_call_optimization_function` and `CM_call_optimization_function.py` are the files that are edited by the user. It calls the `full_optimization.py` file and runs the optimization routine with the specs that are mentioned by the user. 


#### Supporting files
1. `pytest` contains `matplotlib` functions which can individually plot data in `.csv` files. Pytest also contains test data in `.csv` files and also a test version of the gradient descent algorithm.

2) ***ocean scripts*** or `.ocn` files exist within this workspace. These are files that will extract the output after cadence simulations and store it in `.csv` or `.txt` files.

***Ocean scripts*** are a neat way to directly operate on data stored in non-readable formats after cadence simulations using ***SpectreRF***. We can use these commands to perform mathematical/scientific operations on data and obtain them in whatever form we like. To know more, [click here](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.eecis.udel.edu/~vsaxena/courses/ece697A/docs/OCEAN%2BReference.pdf&ved=2ahUKEwjPr-a7r6GIAxXwUGcHHSBJB4AQFnoECAoQAQ&usg=AOvVaw3Nm9DP6-TFI5PBWOF5zEp8).

### Key notes
***All python files in this repo are commented to understand the flow of the gradient descent algorithm and how it is being used to optimize the mixer circuit.***

Key aspects of this code can be easily altered to automate the schematic design for any other standard circuit block (LNAs, PAs, OPAMPs, etc.)
