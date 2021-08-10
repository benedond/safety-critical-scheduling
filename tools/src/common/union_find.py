# https://gist.github.com/artkpv/6f0591c01a940d6ebe1344a8efa88847

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
        
    def get_copy(self) -> 'UnionFind':
        uf = UnionFind(len(self._sz))
        uf._id = self._id.copy()
        uf._sz = self._sz.copy()
        uf.cc = self.cc
        return uf

    def _root(self, i):
        j = i
        while (j != self._id[j]):
            self._id[j] = self._id[self._id[j]]
            j = self._id[j]
        return j

    def find(self, p, q):
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
        
# if __name__ == "__main__":
#     uf = UnionFind(5)
#     lst = [(1,2), (3,4), (0,1)]
#     for a,b in lst:
#         uf.union(a,b)
        
#     print(uf._id)
#     print(uf.find(1,2))
#     print(uf.find(0,2))
#     print(uf.find(0,4))
#     print(uf.union(0,3))
#     print(uf.find(1,3))