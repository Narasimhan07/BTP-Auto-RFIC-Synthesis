import matplotlib.pyplot as plt 
import numpy as np
temp_array = np.linspace(-40, 120, 5)
power_tt_lib = np.array([2.89925*1.2, 2.9219*1.2, 2.95098*1.2, 2.98816*1.2, 3.03597*1.2])
power_ff_lib = np.array([2.94357*1.2, 2.98392*1.2, 3.03619*1.2, 3.104*1.2, 3.19394*1.2])
power_ss_lib = np.array([2.87079*1.2, 2.88633*1.2, 2.90521*1.2, 2.92875*1.2, 2.95832*1.2]) 
fig, ax = plt.subplots()
ax.plot(temp_array, power_tt_lib, linewidth=1.0, linestyle='solid', color='blue', label="Process: tt")
ax.plot(temp_array, power_ff_lib, linewidth=1.0, linestyle='solid', color='red', label="Process: ff")
ax.plot(temp_array, power_ss_lib, linewidth=1.0, linestyle='solid', color='green', label="Process: ss")
ax.grid()
ax.legend(loc=0)
ax.set(xlim=(-40, 120), ylim=(3.3, 3.9), yticks=np.linspace(3.3, 3.9, 7), 
    xticks=np.linspace(-40, 120, 5), xlabel="Temperature in $^{\circ}$ C", ylabel="Power consumption (in mW)", 
    title="Voltage Mode Passive Mixer: Power consumption vs Temp"
    )
plt.show()