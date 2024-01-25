import sys
import json
import random
import heapq


class Graph:
    def __init__(self, n, edges):
        self.n = n
        self.edges = set(tuple(sorted((x, y))) for x, y in edges)
        self.adj_mat = create_adj_mat(self)
        self.adj_list = create_adj_list(self)

    def remove_edge(self, a, b):
        a, b = sorted((a, b))
        self.edges.discard((a, b))
        self.adj_mat[a][b] = 0
        self.adj_mat[b][a] = 0
        self.adj_list[a].discard(b)
        self.adj_list[b].discard(a)

    def add_edge(self, a, b):
        a, b = sorted((a, b))
        self.edges.add((a, b))
        self.adj_mat[a][b] = 1
        self.adj_mat[b][a] = 1
        self.adj_list[a].add(b)
        self.adj_list[b].add(a)

    def get_max_degree(self):
        return max([len(self.adj_list[i]) for i in range(self.n)])

    def copy(self):
        return Graph(self.n, self.edges.copy())

    def get_degree(self, v):
        return len(self.adj_list[v])

    def is_edge(self, a, b):
        return self.adj_mat[a][b] == 1


def create_adj_mat(graph: Graph):
    adj_mat = [[0 for i in range(graph.n)] for j in range(graph.n)]
    for edge in graph.edges:
        adj_mat[edge[0]][edge[1]] = 1
        adj_mat[edge[1]][edge[0]] = 1

    return adj_mat


def create_adj_list(graph: Graph):
    adj_list = [set() for i in range(graph.n)]
    for edge in graph.edges:
        adj_list[edge[0]].add(edge[1])
        adj_list[edge[1]].add(edge[0])

    return adj_list


def bfs(graph: Graph, start, end):
    """Determines whether start and end are connected in graph"""
    visited = [False for i in range(graph.n)]
    queue = [start]
    visited[start] = True

    while len(queue) > 0:
        node = queue.pop(0)
        if node == end:
            return True

        for neighbor in graph.adj_list[node]:
            if not visited[neighbor]:
                queue.append(neighbor)
                visited[neighbor] = True

    return False


def random_shuffle_sparsify(graph: Graph):
    """Randomly removes edges from graph"""
    graph = graph.copy()
    edges = list(graph.edges)
    random.shuffle(edges)

    for edge in edges:
        graph.remove_edge(edge[0], edge[1])
        if not bfs(graph, edge[0], edge[1]):
            # edge cannot be removed...
            graph.add_edge(edge[0], edge[1])

    return graph


def largest_degree_sparisfy_2(graph: Graph):
    """Sparsify the graph by prioritizing edges adjacent to vertices with high degree"""
    graph = graph.copy()
    edges = list(graph.edges)
    edges.sort(
        key=lambda edge: -(graph.get_degree(edge[0]) + graph.get_degree(edge[1]))
    )

    for edge in edges:
        graph.remove_edge(edge[0], edge[1])
        if not bfs(graph, edge[0], edge[1]):
            # edge cannot be removed...
            graph.add_edge(edge[0], edge[1])

    assert len(graph.edges) <= graph.n - 1
    return graph


def largest_degree_sparisfy(graph: Graph):
    """Sparsify the graph by first removing edges from vertices with largest degree"""
    graph = graph.copy()
    # add all the vertices to a heap
    vertices_heap = []
    for vertex in range(graph.n):
        heapq.heappush(vertices_heap, (-graph.get_degree(vertex), vertex))

    while len(vertices_heap) > 0:
        degree, vertex = heapq.heappop(vertices_heap)
        degree = -degree
        assert degree >= graph.get_degree(vertex)

        if degree < graph.get_degree(vertex):
            # add vertex back to the heap and process later
            heapq.heappush(vertices_heap, (-graph.get_degree(vertex), vertex))
            continue

        for neighbor in graph.adj_list[vertex]:
            graph.remove_edge(vertex, neighbor)
            if not bfs(graph, vertex, neighbor):
                # edge cannot be removed...
                graph.add_edge(vertex, neighbor)
            else:
                # add the vertex back to the heap with the new degree
                heapq.heappush(vertices_heap, (-graph.get_degree(vertex), vertex))
                break
        else:
            # no edges were removed, cannot optimize further
            break

    return graph


def add_random_edges(graph: Graph, edges: set, mu=1):
    for edge in edges:
        # if the edge is not in the graph add it with probability mu/n
        if not graph.is_edge(edge[0], edge[1]) and random.random() < mu / len(edges):
            graph.add_edge(edge[0], edge[1])


def sparsify_with_random_edges(graph: Graph, callback, mu=10):
    """Runs the euristhic multiple times, picks the best result"""
    edges = list(graph.edges)
    best_graph = graph.copy()

    for _ in range(10):
        graph = callback(graph)

        if graph.get_max_degree() < best_graph.get_max_degree():
            print("current best...", graph.get_max_degree(), file=sys.stderr)
            best_graph = graph.copy()

        add_random_edges(graph, edges, mu)

    return random_shuffle_sparsify(best_graph)


def main():
    graph = json.load(sys.stdin)
    graph = Graph(graph["n"], graph["edges"])

    results = []

    results.append(("graph", graph.get_max_degree()))
    print(
        f"graph {graph.get_max_degree()}",
        f"with {len(graph.edges)} edges",
        file=sys.stderr,
    )

    sparsified = random_shuffle_sparsify(graph)
    results.append(("random_shuffle_sparsify", sparsified.get_max_degree()))
    print(
        f"random_shuffle_sparsify {sparsified.get_max_degree()}",
        f"with {len(sparsified.edges)} edges",
        file=sys.stderr,
    )

    sparsified = largest_degree_sparisfy_2(graph)
    results.append(("largest_degree_sparisfy_2", sparsified.get_max_degree()))
    print(
        f"largest_degree_sparisfy_2 {sparsified.get_max_degree()}",
        f"with {len(sparsified.edges)} edges",
        file=sys.stderr,
    )

    sparsified = sparsify_with_random_edges(graph, largest_degree_sparisfy_2, 10)
    results.append(("largest_degree_sparisfy_2 + rand", sparsified.get_max_degree()))
    print(
        f"largest_degree_sparisfy_2 + rand {sparsified.get_max_degree()}",
        f"with {len(sparsified.edges)} edges",
        file=sys.stderr,
    )

    sparsified = sparsify_with_random_edges(graph, largest_degree_sparisfy, 10)
    results.append(("largest_degree_sparisfy + rand", sparsified.get_max_degree()))
    print(
        f"largest_degree_sparisfy + rand {sparsified.get_max_degree()}",
        f"with {len(sparsified.edges)} edges",
        file=sys.stderr,
    )

    json.dump(results, sys.stdout)


if __name__ == "__main__":
    main()
