import numpy as np
import matplotlib.pyplot as plt

max_iteration = 20 
alpha_start_log = 0.1
alpha_end_log = 0.001
alpha_start = 0.1
alpha_end = 0.001
iter_number = 1
i = np.arange(1,max_iteration+1)
alpha = []
alpha_linear = []
while iter_number<=max_iteration:
    alpha_linear_i = alpha_start + (((alpha_end - alpha_start)*(iter_number - 1))/(max_iteration-1))
    alpha_log = alpha_start_log + ((alpha_end_log - alpha_start_log)*(iter_number - 1)/(max_iteration-1))
    #alpha_i = np.exp(alpha_log)
    iter_number+=1
    alpha.append(alpha_i)
    alpha_linear.append(alpha_linear_i)
fig, ax = plt.subplots()
ax.plot(i, alpha_linear, linewidth=2.0, linestyle='solid', color='blue')
ax.set(ylim=(0.001, 0.1))
ax.grid()
plt.show()
