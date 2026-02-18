Neighborhood = dict[int, set[int]]


def isNeighborhoodCorrect(neighborhood: Neighborhood) -> bool:
    all_nodes = set(neighborhood.keys())
    for neighbors in neighborhood.values():
        if not neighbors.issubset(all_nodes):
            return False
    return True


def isUndirected(neighborhood: Neighborhood) -> bool:
    if not isNeighborhoodCorrect(neighborhood):
        return False
    for node, neighbors in neighborhood.items():
        for neighbor in neighbors:
            if node not in neighborhood.get(neighbor, set()):
                return False
    return True


def isTree(neighborhood: Neighborhood) -> bool:
    if not neighborhood:
        return False
    if not isUndirected(neighborhood):
        return False

    nodes = list(neighborhood.keys())
    visited = set()

    def has_cycle(u, p):
        visited.add(u)
        for v in neighborhood[u]:
            if v == p:
                continue
            if v in visited:
                return True
            if has_cycle(v, u):
                return True
        return False

    if has_cycle(nodes[0], -1):
        return False

    return len(visited) == len(nodes)


# Illustration of the code work

if __name__ == "__main__":
    # 1. Correct Undirected Tree (Line Topology)
    # 1 --- 2 --- 3
    tree_net = {1: {2}, 2: {1, 3}, 3: {2}}

    # 2. Undirected Graph with Cycle (Ring Topology)
    # 1 --- 2
    # |     |
    # 4 --- 3
    ring_net = {1: {2, 4}, 2: {1, 3}, 3: {2, 4}, 4: {1, 3}}

    # 3. Directed Graph (Asymmetric)
    # 1 ---> 2
    directed_net = {1: {2}, 2: set()}

    # 4. Incorrect Neighborhood (Reference to non-existent node 3)
    broken_net = {1: {2, 3}, 2: {1}}

    graphs = [
        ("Tree Network", tree_net),
        ("Ring Network", ring_net),
        ("Directed Network", directed_net),
        ("Broken Network", broken_net)
    ]

    print(f"{'Network Type':<20} | {'Correct?':<10} | {'Undirected?':<12} | {'Is Tree?':<10}")
    print("-" * 65)

    for name, g in graphs:
        correct = isNeighborhoodCorrect(g)
        undirected = isUndirected(g)
        tree = isTree(g)
        print(f"{name:<20} | {str(correct):<10} | {str(undirected):<12} | {str(tree):<10}")