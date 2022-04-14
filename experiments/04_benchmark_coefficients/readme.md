
# Benchmark coefficients experiment

The purpose of this experiment is to measure the `activity` and `offset` coefficients of the benchmarks. 

Each benchmark is executed at each computing cluster at one/all core(s). The power consumption is measured and the coefficients are then computed based on the results.

 - the activity is the slope of the linear segment linking (1, power at one core) and (n-cores, power at n-cores) points
 - the offset is the offset of the same linear segment (w.r.t. the platforms idle power).
 

