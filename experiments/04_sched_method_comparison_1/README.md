# Comparison of scheduling methods 01

### Notes

 - <b>OPTIMAL2 (predictor) schedules were computed incorrectly (not in accordance with problem statement)</b>

 - fan settings of 0.2 was used during all measurements - <i>this resulted in the fan not being enabled at all</i>

 - each measurement ran for 15 minutes <b>which was insufficient for T_inf to stabilize</b>

 - both A53 and A72 processors were clocked at 600 MHz

 - only difference between INPUT1 and INPUT2 files is problemVersion - for problemVersion=1, the E_ik method was used (resulting in the OPTIMAL1 schedule), for problemVersion=2 the predictor method was used (resulting in the OPTIMAL2 schedule);
  - for the E_ik method, E_ik = (a_ik + b_ik/c_k)\*p_ik, where a_ik is the slope of task i on resource k, b_ik is the intercept of task i on resource k, c_k is the capacity of resource k, p_ik is the processing time of task i on resource k

 - RA+LTF stands for "random assignment + longest tasks first"; in all instances for these schedules the same resource assignment as in the "RANDOM1" schedule was used

 - In instances 2 and 3, the optimality of the OPTIMAL2 schedule is not proven - the schedule is the best gurobi computed after 2 hours on the optim server

 - T_inf was calculated as the average of the last 50 measured values of CPU_0_temp, ambient temperature as the average of the last 5 measured values of ambient, relative T_inf as T_inf minus ambient temperature