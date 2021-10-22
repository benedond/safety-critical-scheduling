
# Experiment: comparison of BAP, BAP with depth limit and ILP on larger instances

We tested instances with $n \in {35, 45, 55, 100}$ tasks. For each $n$, 10 instances were generated. Each solver was executed with timelimit of 600 seconds.

ILP global solver is compared to BAP solver (branching on supports) and BAP solver with depth limit of 20 % of tasks (after this depth is reacher, the node is solved by ILP solver).

|     | ILP      |           | BAP      |           |                              | BAP with limit |           |                              |
|-----|----------|-----------|----------|-----------|------------------------------|----------------|-----------|------------------------------|
| n   | avg time | #timeouts | avg time | #timeouts | relative gap (w.r.t. global) | avg time       | #timeouts | relative gap (w.r.t. global) |
| 35  | 47       | 0         | 386      | 5         | 0.33                         | 259            | 0         | 0.00                         |
| 45  | 446      | 6         | 601      | 10        | 1.07                         | 591            | 9         | 1.01                         |
| 55  | 600      | 10        | 602      | 10        | 0.28                         | 601            | 10        | 0.24                         |
| 100 | 600      | 10        | 604      | 10        | -0.34                        | 603            | 10        | -0.34                        |

On instances with 35 tasks, ILP model outperformed both tested BAP variants having 7.2 and 4.5 lower average time compared to BAP and BAP with limit, respectively. Both ILP and BAP with limit solved all instances to optimality within given time limit. Simple BAP failed to solve half of the instances within 600 seconds.

For instances with 45 tasks, ILP timeoutes on 6 instances, BAP on all 10 instances, and BAP with limit on 9 instances. Still, BAP and BAP with limit provide the same or inferior schedules, compared with ILP. The average gap is 1.07 % for BAP and 1.01 % for BAP with limit, compared to the objectives provided by ILP. 

Starting from instances with 55 tasks, all the solvers timeout on all of the instances. Still, ILP provides the best result on 8 out of 10 instances. Overall, BAP has 0.28 % gap, and BAP with limit has 0.24 % gap.

Finally considering instances with 100 tasks, ILP starts to get inferior - producing 0.42 % worse results compared to both BAP and BAP with limit. However, the best-found results produced by both BAP and BAP with limit are essentially the integer reconstructions of the relaxed solutions in the root node; BAP procedure itself cannot improve this heuristic solution in the given timelimit. I feel that BAP would still be inferior to ILP if the timelimit was longer (or if the ILP would be started with the same heuristic solution). 