import os
# import random
#import pandas as pd
#import numpy as np
#import re

#D = []

def edit_spice_file(file_path,parameter_to_edit,new_value,append_value=True):
	with open(file_path, 'r') as file:
		spice_content = file.readlines()
		# print(spice_content)
		new_line = ""
		spice_new_content = list()
		for line in spice_content:
			line = line.strip()
			words = line.split(' ')
			word1 = words[-1].split('=')[0]
			if(words[0] == 'parameters' and word1 == parameter_to_edit):
				# print(words)
				old_value = float(words[-1].split('=')[-1])
				if(append_value):
					newest_value = parameter_to_edit+"="+str(old_value + new_value)
				else:
					newest_value = parameter_to_edit+"="+str(new_value)
	
				del(words[-1])
				words.append(newest_value)
				new_line = ' '.join(words)
				# print(new_line)
				spice_new_content.append(new_line+" \n")
			else:
				spice_new_content.append(line+" \n")
		# print(spice_new_content)
	with open(file_path, 'w') as file:
		file.writelines(spice_new_content)


phase_out_2 = []
S21_deg = -100
E = []
param_value16_2 = [2.8,2.8,3,3.1,3.2,3.32,3.42,3.52,3.62,3.72,3.82,3.92,4.02,4.12,4.22,4.32]
spice_file_path_2 = 'circ_2.scs'
param_value16 = param_value16_2.copy()

for i in range(16):
	parameter_to_edit="Vsw"+str(i)
	# print(parameter_to_edit)
	initial_value = 0
	edit_spice_file(spice_file_path_2,parameter_to_edit,initial_value,False)

for i in range(16):
	parameter_to_edit="a"+str(i)
	param_value = param_value16_2[i]
	edit_spice_file(spice_file_path_2,parameter_to_edit,param_value,False)
	
os.system("spectre circ_2.scs =log circ_log.txt")

		
with open("sp.out", 'r') as f:
	E =[]
	for line in f:
		row = [item.strip() for item in line.split()]
		E.append(row)
			#print(E[12])
	phase_ini = float(E[12][4])

for i in range(17):
    j = (phase_ini*180/3.1415)-i*90/16
    if(j<-180):
        j = j + 360
    phase_out_2.append(j*3.14/180)

err_margin = 1*3.14/(180)
# print(phase_out_2, err_margin)


for ij in range(1):
	print("ij = ",ij)
	for i in range(16):
		parameter_to_edit="Vsw"+str(i)
		# print(parameter_to_edit)
		initial_value = 0
		edit_spice_file(spice_file_path_2,parameter_to_edit,initial_value,False)

	for i in range(0,16):

		parameter_to_edit="Vsw"+str(i)
		value = 1.2
		edit_spice_file(spice_file_path_2,parameter_to_edit,value)

		iter = 0
		#param_value = param_value16_2[i]
		print("i",i," ")
		target_phase = phase_out_2[i+1]

		while((S21_deg<=(target_phase-err_margin) or (S21_deg>=target_phase+err_margin)) and iter < 20):
			D = []
			print("iter",iter,".........", "target_phase = ",phase_out_2[i+1]*(180/3.14), "Current Phase = ", S21_deg*(180/3.14))
		
			iter = iter + 1
			if((S21_deg*target_phase)<0):
				if(S21_deg<0):
					S21_deg = S21_deg + (2*3.14)
				else:
					S21_deg = S21_deg - (2*3.14)

			z = S21_deg - target_phase
			a = z/err_margin
			if(a>0):
				a = -1*a			
				param_value_increment = 0.2 * (1-((2.7)**(a)))
			else:
				param_value_increment = -0.2 * (1-((2.7)**(a)))
			
			parameter_to_edit="a"+str(i)
			param_value16[i] += param_value_increment
			#param_value = param_value + param_value_increment
			edit_spice_file(spice_file_path_2,parameter_to_edit,param_value_increment)
	
			os.system("spectre circ_2.scs =log circ_log.txt")
			
			with open("sp.out", 'r') as f:
				for line in f:
					row = [item.strip() for item in line.split()]
					D.append(row)
				#print(D[12])
				S21_deg = float(D[12][4])
"""	
for i in range(16):
	parameter_to_edit="Vsw"+str(i)
	# print(parameter_to_edit)
	initial_value = 0
	edit_spice_file(spice_file_path_2,parameter_to_edit,initial_value,False)

for i in range(16):
	parameter_to_edit="Vsw"+str(i)
	value = 1.2
	edit_spice_file(spice_file_path_2,parameter_to_edit,value)
	os.system("spectre circ_2.scs =log circ_log.txt")
	D = []
	with open("sp.out", 'r') as f:
		for line in f:
			row = [item.strip() for item in line.split()]
			D.append(row)
			#print(D[12])
		S21_deg = float(D[12][4])
	print("Phase_out = ",S21_deg*(180/3.14),"target_phase = ",phase_out_2[i+1]*(180/3.14))
"""
print("Param value = ",param_value16)




