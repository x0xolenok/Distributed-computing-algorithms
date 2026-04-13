import collections

class TreeWaveNode:
    def __init__(self, node_id, neighbors):
        self.node_id = node_id
        self.neighbors = set(neighbors)
        self.received_from = set()
        self.sent = False
        self.decided = False
        self.messages_to_send = []

    def receive(self, sender_id):
        self.received_from.add(sender_id)

    def step(self):
        if self.decided:
            return

        if len(self.received_from) == len(self.neighbors):
            self.decided = True
            return

        if len(self.received_from) == len(self.neighbors) - 1 and not self.sent:
            target = (self.neighbors - self.received_from).pop()
            self.messages_to_send.append((target, self.node_id))
            self.sent = True


class TreeWaveSimulator:
    def __init__(self, graph):
        self.nodes = {u: TreeWaveNode(u, neighbors) for u, neighbors in graph.items()}
        self.message_queue = collections.deque()

    def run(self):
        for node in self.nodes.values():
            node.step()
            while node.messages_to_send:
                target, sender = node.messages_to_send.pop(0)
                self.message_queue.append((target, sender))

        step_count = 0
        while self.message_queue:
            step_count += 1
            target, sender = self.message_queue.popleft()
            self.nodes[target].receive(sender)

            self.nodes[target].step()
            while self.nodes[target].messages_to_send:
                new_target, new_sender = self.nodes[target].messages_to_send.pop(0)
                self.message_queue.append((new_target, new_sender))

        decided_nodes = [n.node_id for n in self.nodes.values() if n.decided]
        return step_count, decided_nodes


class EchoNode:
    def __init__(self, node_id, neighbors, is_initiator=False):
        self.node_id = node_id
        self.neighbors = set(neighbors)
        self.is_initiator = is_initiator
        self.parent = None
        self.messages_received = 0
        self.decided = False
        self.messages_to_send = []
        self.active = False

    def start(self):
        if self.is_initiator:
            self.active = True
            for neighbor in self.neighbors:
                self.messages_to_send.append((neighbor, self.node_id))

    def receive(self, sender_id):
        self.messages_received += 1
        if not self.active and not self.is_initiator:
            self.active = True
            self.parent = sender_id
            for neighbor in self.neighbors:
                if neighbor != self.parent:
                    self.messages_to_send.append((neighbor, self.node_id))

    def step(self):
        if not self.decided:
            if self.is_initiator and self.messages_received == len(self.neighbors):
                self.decided = True
            elif not self.is_initiator and self.active and self.messages_received == len(self.neighbors):
                self.messages_to_send.append((self.parent, self.node_id))
                self.decided = True


class EchoSimulator:
    def __init__(self, graph, initiator):
        self.initiator = initiator
        self.nodes = {u: EchoNode(u, neighbors, u == self.initiator) for u, neighbors in graph.items()}
        self.message_queue = collections.deque()

    def run(self):
        self.nodes[self.initiator].start()
        while self.nodes[self.initiator].messages_to_send:
            target, sender = self.nodes[self.initiator].messages_to_send.pop(0)
            self.message_queue.append((target, sender))

        step_count = 0
        while self.message_queue:
            step_count += 1
            target, sender = self.message_queue.popleft()

            self.nodes[target].receive(sender)
            self.nodes[target].step()

            while self.nodes[target].messages_to_send:
                new_target, new_sender = self.nodes[target].messages_to_send.pop(0)
                self.message_queue.append((new_target, new_sender))

        return step_count, self.nodes[self.initiator].decided


def test_simulators():
    tree_graph = {
        1: [2, 3],
        2: [1, 4, 5],
        3: [1],
        4: [2],
        5: [2]
    }

    general_graph = {
        1: [2, 3],
        2: [1, 3, 4],
        3: [1, 2, 4],
        4: [2, 3]
    }

    print("Testing Tree Wave Algorithm:")
    wave_sim = TreeWaveSimulator(tree_graph)
    wave_steps, wave_decided = wave_sim.run()
    print(f"Simulation completed in {wave_steps} steps.")
    print(f"Nodes that decided: {wave_decided}\n")

    print("Testing Echo Algorithm:")
    initiator_node = 1
    echo_sim = EchoSimulator(general_graph, initiator=initiator_node)
    echo_steps, echo_is_decided = echo_sim.run()
    print(f"Simulation completed in {echo_steps} steps.")
    print(f"Initiator {initiator_node} decided: {echo_is_decided}")


if __name__ == "__main__":
    test_simulators()