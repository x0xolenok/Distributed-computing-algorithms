import collections


class EchoExtinctionNode:
    def __init__(self, node_id, neighbors, is_initiator=False):
        self.node_id = node_id
        self.neighbors = set(neighbors)
        self.is_initiator = is_initiator
        self.l = self.node_id if is_initiator else 0
        self.parent = None
        self.expected_echoes = 0
        self.messages_to_send = []
        self.decided = False
        self.is_leader = False

    def start(self):
        if self.is_initiator:
            self.l = self.node_id
            self.expected_echoes = len(self.neighbors)
            for neighbor in self.neighbors:
                self.messages_to_send.append((neighbor, self.node_id, 'explore', self.l))

    def receive(self, sender_id, msg_type, wave_id):
        if msg_type == 'explore':
            if wave_id > self.l:
                self.l = wave_id
                self.parent = sender_id
                self.expected_echoes = len(self.neighbors) - 1

                for neighbor in self.neighbors:
                    if neighbor != self.parent:
                        self.messages_to_send.append((neighbor, self.node_id, 'explore', self.l))

                if self.expected_echoes == 0:
                    self.messages_to_send.append((self.parent, self.node_id, 'echo', self.l))

            elif wave_id == self.l:
                self.messages_to_send.append((sender_id, self.node_id, 'echo', self.l))

        elif msg_type == 'echo':
            if wave_id == self.l:
                self.expected_echoes -= 1
                if self.expected_echoes == 0:
                    if self.parent is not None:
                        self.messages_to_send.append((self.parent, self.node_id, 'echo', self.l))
                    elif self.l == self.node_id:
                        self.is_leader = True
                        self.decided = True


class EchoExtinctionSimulator:
    def __init__(self, graph, initiators):
        self.nodes = {u: EchoExtinctionNode(u, neighbors, u in initiators) for u, neighbors in graph.items()}
        self.queue = collections.deque()

    def run(self):
        for node in self.nodes.values():
            if node.is_initiator:
                node.start()
                while node.messages_to_send:
                    target, sender, mtype, wid = node.messages_to_send.pop(0)
                    self.queue.append((target, sender, mtype, wid))

        steps = 0
        while self.queue:
            target, sender, mtype, wid = self.queue.popleft()
            self.nodes[target].receive(sender, mtype, wid)
            steps += 1

            while self.nodes[target].messages_to_send:
                ntarget, nsender, nmtype, nwid = self.nodes[target].messages_to_send.pop(0)
                self.queue.append((ntarget, nsender, nmtype, nwid))

        leaders = [n.node_id for n in self.nodes.values() if n.is_leader]
        return steps, leaders


def test_simulators():
    graph = {
        1: [2, 3],
        2: [1, 3, 4],
        3: [1, 2, 4],
        4: [2, 3]
    }

    initiators = [1, 2, 4]

    print("Testing Echo Algorithm with Extinction:")
    print(f"Initiators: {initiators}")

    sim = EchoExtinctionSimulator(graph, initiators)
    steps, leaders = sim.run()

    print(f"Simulation completed in {steps} steps.")
    print(f"Elected Leader(s): {leaders}\n")

    print("Final wave IDs per node:")
    for node_id, node in sim.nodes.items():
        role = "Leader" if node.is_leader else "Follower"
        print(f"Node {node_id}: Wave ID = {node.l} ({role})")


if __name__ == "__main__":
    test_simulators()