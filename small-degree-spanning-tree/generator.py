import sys
import json
import argparse
import random
from itertools import tee


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def gnp(n, p):
    edges = set()
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                edges.add((i, j))

    return edges


def dfs(n, edges, node):
    visited = [False for i in range(n)]
    ff = [node]
    visited[node] = True

    while len(ff) > 0:
        i = ff.pop()
        for j in range(n):
            if (i, j) in edges:
                if visited[j]:
                    continue

                visited[j] = True
                ff.append(j)

    return visited


def get_connected_components(n, edges):
    ccs = [None for _ in range(n)]
    cc = 0

    for i in range(n):
        if ccs[i] is not None:
            continue

        visited = dfs(n, edges, i)
        for j, v in enumerate(visited):
            if not v:
                continue

            ccs[j] = cc

    return ccs


def hamiltonian_graph(n):
    edges = set()
    order = list(range(n))
    random.shuffle(order)
    for i, j in pairwise(order):
        edges.add((i, j))

    return edges


def star_graph(n, edges_count):
    star_center = random.randint(0, n - 1)
    edges = set()

    vertices = list(range(n))
    vertices.remove(star_center)
    random.shuffle(vertices)
    for i in range(edges_count):
        edges.add((star_center, vertices[i]))

    return edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--mu", type=float, default=10)
    parser.add_argument("--hamiltonian", action="store_true")
    parser.add_argument("--star", action="store_true")
    args = parser.parse_args()

    n = args.n
    mu = args.mu
    edges = gnp(n, mu / n)

    if args.hamiltonian:
        # add an extra hamiltonian graph to the existing edges
        edges |= hamiltonian_graph(n)

    if args.star:
        # add an extra star graph to the existing edges
        edges |= star_graph(n, n - 1)

    ccs = get_connected_components(n, edges)

    # pick the largest connected component
    vertices_by_cc = [0 for _ in range(n)]
    largest_cc = 0
    for i, cc in enumerate(ccs):
        vertices_by_cc[cc] += 1
        if vertices_by_cc[cc] > vertices_by_cc[largest_cc]:
            largest_cc = cc

    # remove all edges that are not in the largest connected component
    edges = set(
        filter(
            lambda edge: ccs[edge[0]] == largest_cc,
            edges,
        )
    )

    n = vertices_by_cc[largest_cc]

    json.dump(
        {
            "n": n,
            "edges": list(edges),
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
