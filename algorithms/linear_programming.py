from .base_algorithm import *
from cvxopt import matrix, glpk, solvers
from itertools import chain, combinations
from numpy import concatenate, eye, float, full, ones, vstack, zeros

class LinearProgramming(BaseAlgorithm):
    
    def edges_to_tour(self, edges):
        tour, current = [], None
        while edges:
            if current:
                for edge in edges:
                    if current not in edge:
                        continue
                    current = edge[0] if current == edge[1] else edge[1]
                    tour.append(current)
                    edges.remove(edge)
            else:
                x, y = edges.pop()
                tour.extend([x, y])
                current = y
        return tour[:-1]
    
    def ILP_solver(self):
        n, sx = len(distances), len(distances)*(len(distances) - 1)//2
        c = [float(distances[i+1][j+1]) for i in range(n) for j in range(i + 1, n)]
        G, h, b = [], [], full(n, 2, dtype=float)
        for st in list(chain.from_iterable(combinations(range(n), r) for r in range(2, n))):
            G += [[float(i in st and j in st) for i in range(n) for j in range(i + 1, n)]]
            h.append(-float(1 - len(st)))
        A = [[float(k in (i, j)) for i in range(n) for j in range(i + 1, n)] for k in range(n)]
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
        _, x = glpk.ilp(c, G.T, h, A.T, b, B=set(range(sx)))
        reverse_mapping = [(i+1, j+1) for i in range(n) for j in range(i + 1, n)]
        tour = self.edges_to_tour([reverse_mapping[k] for k in range(sx) if x[k]])
        return self.format_solution(tour), [self.compute_length(tour)]*n