import collections


class LaiYangNode:
    def __init__(self, node_id, neighbors):
        self.node_id = node_id
        self.neighbors = set(neighbors)
        self.color = "white"
        self.local_state = 0
        self.saved_state = None
        self.transit_messages = collections.defaultdict(list)

    def snapshot(self):
        if self.color == "white":
            self.color = "red"
            self.saved_state = self.local_state

    def receive(self, sender, payload, msg_color):
        if self.color == "white" and msg_color == "red":
            self.snapshot()

        if self.color == "red" and msg_color == "white":
            self.transit_messages[sender].append(payload)

        self.local_state += payload


class LaiYangSimulator:
    def __init__(self, graph):
        self.nodes = {u: LaiYangNode(u, neighbors) for u, neighbors in graph.items()}
        self.queue = collections.deque()

    def dispatch(self, sender, target, payload):
        msg_color = self.nodes[sender].color
        self.queue.append((target, sender, payload, msg_color))

    def run(self):
        steps = 0
        while self.queue:
            target, sender, payload, msg_color = self.queue.popleft()
            self.nodes[target].receive(sender, payload, msg_color)
            steps += 1
        return steps


def test_simulators():
    graph = {
        1: [2, 3],
        2: [1, 3],
        3: [1, 2]
    }

    sim = LaiYangSimulator(graph)

    sim.nodes[1].local_state = 100
    sim.nodes[2].local_state = 200
    sim.nodes[3].local_state = 300

    sim.dispatch(1, 2, 10)
    sim.dispatch(3, 2, 50)

    sim.nodes[2].snapshot()

    sim.dispatch(2, 1, 20)

    sim.nodes[3].snapshot()

    sim.dispatch(1, 3, 5)

    sim.run()

    print("Lai-Yang Snapshot Algorithm Results:\n")
    for node_id, node in sim.nodes.items():
        print(f"Node {node_id}:")
        print(f"  Final State: {node.local_state}")
        print(f"  Saved State: {node.saved_state}")
        transit = dict(node.transit_messages) if node.transit_messages else "None"
        print(f"  Transit Messages: {transit}\n")


if __name__ == "__main__":
    test_simulators()