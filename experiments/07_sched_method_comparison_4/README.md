# Comparison of scheduling methods 03

### Notes

 - fan was disabled during all measurements

 - each measurement ran for 30 minutes 

 - A53 was clocked at 1200 MHz, A72 at 1596 MHz

 - T_inf was calculated as the average of the last 50 measured values of CPU_0_temp, ambient temperature as the average of the last 5 measured values of ambient, relative T_inf as T_inf minus ambient temperature

 schedules:

| Identifier        | Resource assignment           | Schedule  |
| ------------- |-------------| -----|
| antiEiko       |anti-Optimal (E_ik method), E_ik = (a_ik + b_ik/c_k)\*p_ik|   min C_max as computed by ILP solver |
| antinobo        |anti-Optimal (E_ik method), E_ik = a_ik\*p_ik|    min C_max as computed by ILP solver |
| antipred |anti-Optimal (predictor method)|    Feasible as computed by ILP solver |
| Eiko  |Optimal (E_ik method), E_ik = (a_ik + b_ik/c_k)\*p_ik|   min C_max as computed by ILP solver |
| nobo |Optimal (E_ik method), E_ik = a_ik\*p_ik|    min C_max as computed by ILP solver |
| pred |Optimal (predictor method)|    As computed by ILP solver |
| RALTF        |same as in RANDOM1|    Longest processing time first |
| RANDOM#      |Random feasible|    Random feasible |