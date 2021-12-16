 using Metaheuristics

n_tasks = 100
values = rand(n_tasks) - 0.5

 
function f(x)     
  fx = (1-x)^2+100(y-x^2)^2        
  return fx
end

bounds = repeat([0 1], n_tasks)

optimize(f, bounds, ECA(N=30, K=3))