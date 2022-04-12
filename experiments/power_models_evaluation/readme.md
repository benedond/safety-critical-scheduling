
# Evaluation of the power models

In this experiment, various power models are tested on a set of instances. 

The tested models are:

 - The empirical SUM-MAX model
 - Linear regression model
 - Linear regression UB
 
A set of simple instances is generated, each instance has a single window in which the tasks of random lengths are randomly allocated to its cores. Each instance is then executed on the physical platforms. The power predictions are then compared with the measured data.

## Experimental folder structure

 - instances : generated set of instances by `generate_instances.sh` (which calls `generate_instances.py`)
 - demos_configurations : `.yaml` files exported from `instances` folder
 - schedules : visualization of the individual instances
 - measurements : data obtained by executing the `demos_configurations` on the physical platform(s)
