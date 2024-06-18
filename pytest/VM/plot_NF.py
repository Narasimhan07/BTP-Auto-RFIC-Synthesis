import matplotlib.pyplot as plt 
import numpy as np
temp_array = np.linspace(-40, 120, 5)
nf_tt_lib = np.array([5.81878, 5.99643, 6.16997, 6.34364, 6.52241])
nf_ff_lib = np.array([6.31676, 6.50235, 6.68158, 6.86174, 7.05256])
nf_ss_lib = np.array([5.55406, 5.72961, 5.90283, 6.07675, 6.25412]) 
fig, ax = plt.subplots()
ax.plot(temp_array, nf_tt_lib, linewidth=1.0, linestyle='solid', color='blue', label="Process: tt")
ax.plot(temp_array, nf_ff_lib, linewidth=1.0, linestyle='solid', color='red', label="Process: ff")
ax.plot(temp_array, nf_ss_lib, linewidth=1.0, linestyle='solid', color='green', label="Process: ss")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(-40, 120), ylim=(5.5, 7.25), yticks=np.linspace(5.5, 7.25, 8), 
    xticks=np.linspace(-40, 120, 5), xlabel="Temperature in $^{\circ}$ C", ylabel="SSB Integrated Noise figure (in dB)", 
    title="Voltage Mode Passive Mixer: SSB Integrated Noise figure vs Temp"
    )
plt.show()