import docplex.cp.modeler as cpmod
from docplex.cp.model import CpoModel
from docplex.cp.model import CpoParameters

m = CpoModel()

w0 = m.interval_var(name="w0")
w1 = m.interval_var(name="w1")
w2 = m.interval_var(name="w2")
w3 = m.interval_var(name="w3")
w4 = m.interval_var(name="w4")

t0 = m.interval_var(optional=True, name="t0", size=77)
t1 = m.interval_var(optional=True, name="t1", size=77)
t2 = m.interval_var(optional=True, name="t2", size=77)
t3 = m.interval_var(optional=True, name="t3", size=77)
t4 = m.interval_var(optional=True, name="t4", size=77)

d0 = m.interval_var(name="d0", size=0)
d1 = m.interval_var(name="d1", size=0)
d2 = m.interval_var(name="d2", size=0)
d3 = m.interval_var(name="d3", size=0)
d4 = m.interval_var(name="d4", size=0)

m.add(cpmod.end_of(w4) <= 99)
m.add(cpmod.end_at_start(w0,w1))
m.add(cpmod.end_at_start(w1,w2))
m.add(cpmod.end_at_start(w2,w3))
m.add(cpmod.end_at_start(w3,w4))
m.add(cpmod.span(w0, [t0,d0]))
m.add(cpmod.span(w1, [t1,d1]))
m.add(cpmod.span(w2, [t2,d2]))
m.add(cpmod.span(w3, [t3,d3]))
m.add(cpmod.span(w4, [t4,d4]))

m.add(cpmod.presence_of(t0) + cpmod.presence_of(t1) + cpmod.presence_of(t2) + cpmod.presence_of(t3) + cpmod.presence_of(t4) == 1)

m.solve()

print(m.refine_conflict())

