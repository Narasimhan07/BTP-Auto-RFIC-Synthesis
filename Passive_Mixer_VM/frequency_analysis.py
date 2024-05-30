# =========================================== POST OPTIMIZATION FREQUENCY ANALYSIS ========================================================
# The inputs to this operation are post optimization circuit parameters and simulation parameters for the frequency analysis to be done
#   1. gain over bandwidth for given flo
#   2. S11 over 2*bandwidth around centre frequency = given flo
#   3. integrated SSB Noise figure from 1K to bandwidth for given flo
#   4. iip3 - for 2 tones & flo specified by the user
#   5. 1-dB compression point 
import numpy as np
import Passive_Mixer_VM.common_functions as cf
# defining the analysis function
def freq_analysis(cir, post_optimization_freq):
    # there are 4 different analysis run in freq_analysis - S11, gain, NF and iip3
    # 1) running S11 sweep
    cf.S11_netlist_edit(post_optimization_freq['flo'], post_optimization_freq['RF_Bandwidth'], 
        cir.post_optimization_circuit_parameters, post_optimization_freq['simulation'], "sweep"
    )
    # after editing the netlist, run the sweep and output in case of S11 is written to "sp_sweep.out"
    cf.run_spectre(post_optimization_freq['simulation']['netlists']['S11_netlist'])
    # the function to extract results for S11_sweep returns freq list and s11 @ each freq list
    freq_list_1, S11_db_list = cf.extract_S11(post_optimization_freq['simulation']['S11']['.out_file_path'], "sweep")
    # INSERT MATPLOTLIB FUNCTION TO PLOT S11
    cf.plot_result(freq_list_1, S11_db_list, "frequency (Hz)", "S11 (dB)", 
    "S11 over bandwidth of I arm at flo = " + str(post_optimization_freq['flo']), "linear"
    )

    # 2) running gain sweep
    cf.gain_netlist_edit(post_optimization_freq['flo'], post_optimization_freq['RF_Bandwidth'], 
        cir.post_optimization_circuit_parameters, post_optimization_freq['simulation'], "sweep"
    )
    # after editing the netlist, run the sweep
    cf.run_spectre_with_PSF_file(post_optimization_freq['simulation']['netlists']['gain_netlist'])
    # the function to extract results for gain_sweep returns freq list and gain @ each freq list
    freq_list_2, gain_db_list = cf.extract_gain(post_optimization_freq['simulation']['gain']['ocean_script'], "sweep")
    # INSERT MATPLOTLIB FUNCTION TO PLOT gain
    cf.plot_result(freq_list_2, gain_db_list, "frequency (Hz)", "gain (dB)",
    "conversion gain of I arm at flo = " + str(post_optimization_freq['flo']), "semilogx"
    )

    # 3) running noise figure
    cf.integrated_NF_netlist_edit(
        post_optimization_freq['flo'], post_optimization_freq['RF_Bandwidth'], cir.post_optimization_circuit_parameters,
        post_optimization_freq['simulation']
    )
    # after editing the netlist, run the sweep
    cf.run_spectre_with_PSF_file(post_optimization_freq['simulation']['netlists']['NF_netlist'])
    # the function to extract results for integrated NF returns freq list and NF @ each freq list
    integ_NF, freq_list_3, NF_db_list = cf.extract_integrated_NF(post_optimization_freq['simulation']['NF']['ocean_script'], True)
    print("Integrated Noise figure at flo = ", post_optimization_freq['flo'], " is = ", integ_NF)
    # INSERT MATPLOTLIB FUNCTION TO PLOT NF
    cf.plot_result(freq_list_3, NF_db_list, "frequency (Hz)", "Noise figure (dB)",
    "SSB Noise figure of I arm at flo = " + str(post_optimization_freq['flo']), "linear"
    )

    # 4) running iip3
    cf.iip3_netlist_edit(
        post_optimization_freq['flo'], cir.post_optimization_circuit_parameters, post_optimization_freq['simulation']
    )
    # after editing the netlist, run the hb analysis
    cf.run_spectre_with_PSF_file(post_optimization_freq['simulation']['netlists']['iip3_netlist'])
    # the function to extract results for iip3 returns a single floating pt iip3 value as output
    iip3_value = cf.extract_iip3(post_optimization_freq['simulation']['iip3']['ocean_script'])
    print("iip3 for the given tones at flo = ", post_optimization_freq['flo'], " is = ", iip3_value)

# END FREQUENCY ANALYSIS
