class DSU:
    def __init__(self, n: int):
        self.p = [i for i in range(n)]
        self.sz = [1 for i in range(n)]

    def get(self, v: int):
        if self.p[v] == v:
            return v

        self.p[v] = self.get(self.p[v])
        return self.p[v]

    def check(self, a: int, b: int):
        return self.get(a) == self.get(b)

    def merge(self, a: int, b: int):
        a = self.get(a)
        b = self.get(b)

        if self.sz[a] < self.sz[b]:
            a, b = b, a

        self.p[b] = a
        self.sz[a] += self.sz[b]
