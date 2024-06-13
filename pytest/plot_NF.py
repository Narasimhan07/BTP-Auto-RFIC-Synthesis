import matplotlib.pyplot as plt 
import numpy as np
temp_array = np.linspace(-40, 120, 5)
nf_tt_lib = np.array([6.76807, 7.01678, 7.26051, 7.50215, 7.745])
nf_ff_lib = np.array([7.22267, 7.4713, 7.70923, 7.94294, 8.17886])
nf_ss_lib = np.array([6.52681, 6.79288, 7.05301, 7.31108, 7.57323]) 
fig, ax = plt.subplots()
ax.plot(temp_array, nf_tt_lib, linewidth=1.0, linestyle='solid', color='blue', label="tt_lib")
ax.plot(temp_array, nf_ff_lib, linewidth=1.0, linestyle='solid', color='red', label="ff_lib")
ax.plot(temp_array, nf_ss_lib, linewidth=1.0, linestyle='solid', color='green', label="ss_lib")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(-40, 120), ylim=(6.5, 8.2), yticks=np.linspace(6.4, 8.2, 10), 
    xticks=np.linspace(-40, 120, 5), xlabel="Temperature in $^{\circ}$ C", ylabel="SSB Integrated Noise figure (in dB)", 
    title="Voltage Mode Passive Mixer: SSB Integrated Noise figure vs Temp"
    )
plt.show()