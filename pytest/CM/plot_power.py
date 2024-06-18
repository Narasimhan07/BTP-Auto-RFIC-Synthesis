import matplotlib.pyplot as plt 
import numpy as np
temp_array = np.linspace(-40, 120, 5)
power_tt_lib = np.array([8.34125*1.2, 8.39977*1.2, 8.42294*1.2, 8.43324*1.2, 8.44585*1.2])
power_ff_lib = np.array([8.14807*1.2, 8.17915*1.2, 8.20843*1.2, 8.24105*1.2, 8.28444*1.2])
power_ss_lib = np.array([8.60392*1.2, 8.55109*1.2, 8.50602*1.2, 8.47596*1.2, 8.46205*1.2]) 
fig, ax = plt.subplots()
ax.plot(temp_array, power_tt_lib, linewidth=1.0, linestyle='solid', color='blue', label="Process: tt")
ax.plot(temp_array, power_ff_lib, linewidth=1.0, linestyle='solid', color='red', label="Process: ff")
ax.plot(temp_array, power_ss_lib, linewidth=1.0, linestyle='solid', color='green', label="Process: ss")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(-40, 120), ylim=(9.7, 10.5), yticks=np.linspace(9.7, 10.5, 9), 
    xticks=np.linspace(-40, 120, 5), xlabel="Temperature in $^{\circ}$ C", ylabel="Power consumption (in mW)", 
    title="Current Mode Passive Mixer: Power consumption vs Temp"
    )
plt.show()