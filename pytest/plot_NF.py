import matplotlib.pyplot as plt 
import numpy as np
temp_array = np.linspace(-40, 120, 5)
nf_tt_lib = np.array([6.36, 6.516, 6.662, 6.804, 6.95])
nf_ff_lib = np.array([7.148, 7.315, 7.468, 7.618, 7.78])
nf_ss_lib = np.array([5.899, 6.05, 6.193, 6.333, 6.473]) 
fig, ax = plt.subplots()
ax.plot(temp_array, nf_tt_lib, linewidth=1.0, linestyle='solid', color='blue', label="tt_lib")
ax.plot(temp_array, nf_ff_lib, linewidth=1.0, linestyle='solid', color='red', label="ff_lib")
ax.plot(temp_array, nf_ss_lib, linewidth=1.0, linestyle='solid', color='green', label="ss_lib")
ax.grid()
ax.legend(loc=1)
ax.set(xlim=(-40, 120), ylim=(5.85, 8), yticks=np.linspace(5.8, 8.2, 7), 
    xticks=np.linspace(-40, 120, 5), xlabel="Temperature in $^{\circ}$ C", ylabel="SSB Integrated Noise figure (in dB)", 
    title="VM Passive Mixer: SSB Integrated noise figure vs Temp"
    )
plt.show()