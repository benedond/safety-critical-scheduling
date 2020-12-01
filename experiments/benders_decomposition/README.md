## Finding a feasible schedule minimizing energy consumption by using Benders' decomposition

Our overall goal is to find a feasible schedule that minimizes energy consumption. However, the global ILP formulation of this problem does not scale well since it requires O(n<sup>2</sup>) binary variables with respect to the number of tasks. One way to overcome this issue is by applying Benders' decomposition and splitting the problem into two parts: assigning tasks to resources (master problem) and creating a schedule with fixed resource assignments (subproblem).

A feasible assignment of resources does not guarantee that it will be possible to create a feasible schedule. Thus it may be required to generate so-called Benders cuts. This means that additional constraints will be added to the master problem after an unsuccessful solution of the subproblem. A new resource assignment will then be found, and an attempt to create a new schedule will be made. This process will continue until either no feasible resource assignment can be found or a feasible schedule is created.

In this experiment, two ways of generating Benders cuts were examined:
 - <i>naive cuts</i>: in each iteration, a constraint forbidding the last resource assignment of all tasks together is added.
 - <i>"better" cuts</i>: in each iteration, a constraint forbidding the last resource assignment of tasks that participate in the IIS (irreducible inconsistent subsystem) of the subproblem is added.

 The approaches mentioned above were tried on two test instances:
  - <code>suboptimal_instance.json</code>: an instance for which a feasible schedule that requires suboptimal resource assignment can be found (it is not possible to create a feasible schedule with optimal resource assignment).
  - <code>infeasible_instance.json</code>: an instance for which no feasible schedule can be found but passes the relaxed constraints of the master problem.

The experiment was conducted with Lua scripts. After verifying the validity of this approach, the ability to generate both types of cuts was added to the ILP solver of phase 2.

### Results
<b>Suboptimal instance:</b>
 - naive cuts: 7 iterations
 - "better" cuts: 4 iterations

<b>Infeasible instance:</b>
 - naive cuts: 200 iterations
 - "better" cuts: 10 iterations

Solution correctness was verified with a global problem solver.