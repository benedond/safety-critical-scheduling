
# Window combinations test

Apparently, the LR model does not work that well on TX2 platform. It seems, that even though the LR coefficients work for simple data for which they were identified, the prediction error increases as soon as the windows become more complex. 

The aim of this experiment is to test, whether this problem is caused exactly by combining the windows (possibly due to aggresive thermal management of TX2?).

One window is generated and split in half. During the first half, both clusters are executing some workload. During the second half, only one of the clusters is executing the workload, the other one is idling. Several configurations are created, including (i) one representing just the first half of the window (to measure the reference), (ii) one representing the seconf half of the window, and (iii) one representing the whole window.
