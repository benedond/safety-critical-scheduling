<h1>Example data</h1>

 - <b>environment.json:</b> environment data that can be used with instance generator.
 - <b>assignment_input.json:</b> input for phase 1 solver that has a feasible solution both in phase 1 and 2.
 - <b>assignment_input_p2_infeasible.json:</b> input for phase 1 solver that has a feasible solution in phase 1, but no feasible solution in phase 2.
 - <b>assignment_input_suboptimal.json:</b> input for phase 1 solver that has a feasible solution in phase 2, which requires suboptimal resouce assignment in phase 1.
 - <b>scheduling_input.json:</b> input for phase 2 solver that has a feasible solution.
 - <b>solution.json:</b> optimal solution for <i>scheduling_input.json</i>.
 - <b>all_fields.json:</b> a JSON that contains all fields that are recognized by the tools in this repository. At the same time it is a complete and optimal solution of the <i>assignment_input_suboptimal.json</i> instance.