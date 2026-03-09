import collections


class AwerbuchDFS:
    def __init__(self, adj, start_node):
        self.adj = adj
        self.start_node = start_node
        self.nodes = {n: {
            'father': None,
            'unvisited': set(adj[n]),
            'flags': {m: 0 for m in adj[n]},
            'visited': False
        } for n in adj}
        self.messages = collections.deque()
        self.tree_edges = []

    def simulate(self):
        self.messages.append((self.start_node, self.start_node, 'DISCOVER'))
        self.nodes[self.start_node]['father'] = self.start_node

        while self.messages:
            sender, receiver, mtype = self.messages.popleft()
            node_data = self.nodes[receiver]

            if mtype == 'DISCOVER':
                if not node_data['visited']:
                    node_data['visited'] = True
                    node_data['father'] = sender
                    if sender != receiver:
                        self.tree_edges.append((sender, receiver))

                    others = [q for q in self.adj[receiver] if q != sender]
                    if not others:
                        self.messages.append((receiver, receiver, 'RETURN'))
                    else:
                        for q in others:
                            self.messages.append((receiver, q, 'VISITED'))
                            node_data['flags'][q] = 1

            elif mtype == 'VISITED':
                if sender in node_data['unvisited']:
                    node_data['unvisited'].remove(sender)
                self.messages.append((receiver, sender, 'ACK'))

            elif mtype == 'ACK':
                node_data['flags'][sender] = 0
                if all(f == 0 for f in node_data['flags'].values()):
                    self.messages.append((receiver, receiver, 'RETURN'))

            elif mtype == 'RETURN':
                targets = [k for k in self.adj[receiver] if k in node_data['unvisited']]
                if targets:
                    k = targets[0]
                    node_data['unvisited'].remove(k)
                    self.messages.append((receiver, k, 'DISCOVER'))
                else:
                    if node_data['father'] != receiver:
                        self.messages.append((receiver, node_data['father'], 'RETURN'))
        return self.tree_edges


class CidonDFS:
    def __init__(self, adj, start_node):
        self.adj = adj
        self.start_node = start_node
        self.nodes = {n: {
            'parent': None,
            'visited': False,
            'neighbors': list(adj[n]),
            'info_received': set()
        } for n in adj}
        self.messages = collections.deque()
        self.tree_edges = []

    def simulate(self):
        self.messages.append((self.start_node, self.start_node, 'TOKEN'))

        while self.messages:
            sender, receiver, mtype = self.messages.popleft()
            node_data = self.nodes[receiver]

            if mtype == 'TOKEN':
                if not node_data['visited']:
                    node_data['visited'] = True
                    node_data['parent'] = sender
                    if sender != receiver:
                        self.tree_edges.append((sender, receiver))

                    for n in self.adj[receiver]:
                        if n != sender:
                            self.messages.append((receiver, n, 'INFO'))

                    self.process_next(receiver)
                else:
                    self.messages.append((receiver, sender, 'BACK'))

            elif mtype == 'INFO':
                node_data['info_received'].add(sender)

            elif mtype == 'BACK':
                self.process_next(receiver)

        return self.tree_edges

    def process_next(self, u):
        node_data = self.nodes[u]
        while node_data['neighbors']:
            v = node_data['neighbors'].pop(0)
            if v != node_data['parent'] and v not in node_data['info_received']:
                self.messages.append((u, v, 'TOKEN'))
                return

        if node_data['parent'] != u and node_data['parent'] is not None:
            self.messages.append((u, node_data['parent'], 'BACK'))


def run_tests():
    # ---------------------------------------------------------
    # TEST CASE 1: Cycle Graph (A-B-D-C-A)
    # ---------------------------------------------------------
    graph_cycle = {
        'A': ['B', 'C'],
        'B': ['A', 'D'],
        'C': ['A', 'D'],
        'D': ['B', 'C']
    }
    print(" Test Case 1: Cycle Graph")

    awerbuch_res = AwerbuchDFS(graph_cycle, 'A').simulate()
    print(f"Awerbuch DFS Tree Edges: {awerbuch_res}")
    assert len(awerbuch_res) == len(graph_cycle) - 1

    cidon_res = CidonDFS(graph_cycle, 'A').simulate()
    print(f"Cidon DFS Tree Edges:    {cidon_res}")
    assert len(cidon_res) == len(graph_cycle) - 1
    print("Result: PASS\n")

    # ---------------------------------------------------------
    # TEST CASE 2: Star Graph
    # ---------------------------------------------------------
    graph_star = {
        'Center': ['1', '2', '3', '4'],
        '1': ['Center'], '2': ['Center'], '3': ['Center'], '4': ['Center']
    }
    print("Test Case 2: Star Graph")

    awerbuch_res = AwerbuchDFS(graph_star, 'Center').simulate()
    print(f"Awerbuch DFS Tree Edges: {awerbuch_res}")
    assert len(awerbuch_res) == 4

    cidon_res = CidonDFS(graph_star, 'Center').simulate()
    print(f"Cidon DFS Tree Edges:    {cidon_res}")
    assert len(cidon_res) == 4
    print("Result: PASS\n")

    # ---------------------------------------------------------
    # TEST CASE 3: Complete Graph (K4)
    # ---------------------------------------------------------
    graph_k4 = {
        '1': ['2', '3', '4'], '2': ['1', '3', '4'],
        '3': ['1', '2', '4'], '4': ['1', '2', '3']
    }
    print("Test Case 3: Complete Graph K4")

    awerbuch_res = AwerbuchDFS(graph_k4, '1').simulate()
    print(f"Awerbuch DFS Tree Edges: {awerbuch_res}")
    assert len(awerbuch_res) == 3

    cidon_res = CidonDFS(graph_k4, '1').simulate()
    print(f"Cidon DFS Tree Edges:    {cidon_res}")
    assert len(cidon_res) == 3
    print("Result: PASS\n")

    print("FINAL STATUS: ALL TESTS PASSED SUCCESSFULLY")



if __name__ == "__main__":
    run_tests()