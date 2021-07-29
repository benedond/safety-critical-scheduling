import itertools 

class UnionFind:
    """Weighted quick-union with path compression and connected components.
    The original Java implementation is introduced at
    https://www.cs.princeton.edu/~rs/AlgsDS07/01UnionFind.pdf
    >>> uf = UnionFind(10)
    >>> for (p, q) in [(3, 4), (4, 9), (8, 0), (2, 3), (5, 6), (5, 9),
    ...                (7, 3), (4, 8), (6, 1)]:
    ...     uf.union(p, q)
    >>> uf._id
    [8, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    >>> uf.find(0, 1)
    True
    >>> uf._id
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    """

    def __init__(self, n):
        self._id = list(range(n))
        self._sz = [1] * n
        self.cc = n  # connected components

    def _root(self, i):
        j = i
        while (j != self._id[j]):
            self._id[j] = self._id[self._id[j]]
            j = self._id[j]
        return j    

    def find(self, p, q):
        """Returns True if roots of p and q are the same"""
        return self._root(p) == self._root(q)

    def union(self, p, q):
        i = self._root(p)
        j = self._root(q)
        if i == j:
            return
        if (self._sz[i] < self._sz[j]):
            self._id[i] = j
            self._sz[j] += self._sz[i]
        else:
            self._id[j] = i
            self._sz[i] += self._sz[j]
        self.cc -= 1
        

on_same = [('task-5', 'task-11'), ('task-12', 'task-3'), ('task-8', 'task-14'), ('task-5', 'task-10'), ('task-7', 'task-12'), ('task-11', 'task-0')]
on_diff = [('task-2', 'task-0'), ('task-13', 'task-7'), ('task-9', 'task-4'), ('task-6', 'task-1'), ('task-11', 'task-2'), ('task-0', 'task-13'), ('task-3', 'task-8'), ('task-14', 'task-9'), ('task-4', 'task-6'), ('task-1', 'task-10'), ('task-5', 'task-2'), ('task-13', 'task-12'), ('task-7', 'task-8'), ('task-3', 'task-14'), ('task-9', 'task-6'), ('task-4', 'task-1'), ('task-2', 'task-10'), ('task-5', 'task-13'), ('task-11', 'task-7'), ('task-0', 'task-12'), ('task-3', 'task-9'), ('task-8', 'task-4'), ('task-14', 'task-6'), ('task-5', 'task-1'), ('task-13', 'task-10'), ('task-11', 'task-12'), ('task-2', 'task-7'), ('task-0', 'task-3'), ('task-8', 'task-9'), ('task-14', 'task-4'), ('task-6', 'task-10')]

all_tasks = set()
for a,b in on_same:    
    all_tasks.add(a)
    all_tasks.add(b)
for a,b in on_diff:    
    all_tasks.add(a)
    all_tasks.add(b)

print(all_tasks)

task_to_idx = {t: i for i, t in enumerate(all_tasks)}        
uf = UnionFind(len(all_tasks))

print(task_to_idx)

for a,b in on_same:
    uf.union(task_to_idx[a], task_to_idx[b])      
    
used_by_on_diff = set()
for i,j in on_diff:
    used_by_on_diff.add((uf._root(task_to_idx[i]), uf._root(task_to_idx[j])))  
    used_by_on_diff.add((uf._root(task_to_idx[j]), uf._root(task_to_idx[i])))  

print("USED")
for x in used_by_on_diff:
    print(x)
     
all_pairs = itertools.combinations(all_tasks, 2)  # combine the tasks
all_pairs = [p for p in all_pairs if p not in on_same and p not in on_diff]  # filter already used tasks
all_pairs = [p for p in all_pairs if not uf.find(task_to_idx[p[0]], task_to_idx[p[1]])]  # filter on same components
all_pairs = [p for p in all_pairs if (uf._root(task_to_idx[p[0]]), uf._root(task_to_idx[p[1]])) not in used_by_on_diff]  # filter on diff components

print("All pairs for selection")
print(len(all_pairs))
