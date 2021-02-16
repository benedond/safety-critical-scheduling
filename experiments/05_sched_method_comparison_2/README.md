# Comparison of scheduling methods 02

### Notes

 - fan was disabled during all measurements

 - each measurement ran for 30 minutes 

 - A53 was clocked at 1200 MHz, A72 at 1596 MHz

 - only difference between INPUT1 and INPUT2 files is problemVersion - for problemVersion=1, the E_ik method was used (resulting in the OPTIMAL1 schedule), for problemVersion=2 the predictor method was used (resulting in the OPTIMAL2 schedule);

 - T_inf was calculated as the average of the last 50 measured values of CPU_0_temp, ambient temperature as the average of the last 5 measured values of ambient, relative T_inf as T_inf minus ambient temperature

schedules:

| Identifier        | Resource assignment           | Schedule  |
| ------------- |-------------| -----|
| EikLTF       | Optimal (E_ik method), E_ik = (a_ik + b_ik/c_k)\*p_ik | Longest processing time first|
| EikR1        |Optimal (E_ik method), E_ik = (a_ik + b_ik/c_k)\*p_ik|   Random feasible (each window being as full as possible) |
| OPTIMAL E_ik |Optimal (E_ik method), E_ik = (a_ik + b_ik/c_k)\*p_ik|    Feasible as computed by ILP solver |
| OPTIMAL nob  |Optimal (E_ik method), E_ik = a_ik\*p_ik|   Feasible as computed by ILP solver |
| OPTIMAL nobo |Optimal (E_ik method), E_ik = a_ik\*p_ik|    min C_max as computed by ILP solver |
| OPTIMAL pred |Optimal (predictor method)|    Feasible as computed by ILP solver |
| RALTF        |same as in RANDOM1|    Longest processing time first |
| RANDOM#      |Random feasible|    Random feasible |
