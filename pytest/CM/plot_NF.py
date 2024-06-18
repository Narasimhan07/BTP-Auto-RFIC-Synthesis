import matplotlib.pyplot as plt 
import numpy as np
temp_array = np.linspace(-40, 120, 5)
nf_tt_lib = np.array([6.74483, 7.09145, 7.41211, 7.71102, 7.99267])
nf_ff_lib = np.array([6.79855, 7.14607, 7.46778, 7.76958, 8.05885])
nf_ss_lib = np.array([6.70926, 7.05556, 7.37579, 7.67403, 7.95385]) 
fig, ax = plt.subplots()
ax.plot(temp_array, nf_tt_lib, linewidth=1.0, linestyle='solid', color='blue', label="Process: tt")
ax.plot(temp_array, nf_ff_lib, linewidth=1.0, linestyle='solid', color='red', label="Process: ff")
ax.plot(temp_array, nf_ss_lib, linewidth=1.0, linestyle='solid', color='green', label="Process: ss")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(-40, 120), ylim=(6.7, 8.1), yticks=np.linspace(6.7, 8.1, 8), 
    xticks=np.linspace(-40, 120, 5), xlabel="Temperature in $^{\circ}$ C", ylabel="SSB Integrated Noise figure (in dB)", 
    title="Current Mode Passive Mixer: SSB Integrated Noise figure vs Temp"
    )
plt.show()