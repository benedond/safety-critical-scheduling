using Evolutionary

n_variables = 100

obj(x) = -sum(x)
c1(x) = [ sum(x.^2) - 10 ]

lb = [0.0 for _ in 1:n_variables]
ub = [1.0 for _ in 1:n_variables]

lc = [0.0]
uc = [10.0]

con = WorstFitnessConstraints(lb, ub, lc, uc, c1)

ga = GA(populationSize = 3*n_variables,
        selection=tournament(5), 
        mutation=domainrange([0.5 for _ in 1:n_variables], n_variables),
        crossover=TPX)

x0 =  [0.0 for _ in 1:n_variables]

res = Evolutionary.optimize(obj, con, x0, ga, Evolutionary.Options(abstol=0.005, time_limit=60))





