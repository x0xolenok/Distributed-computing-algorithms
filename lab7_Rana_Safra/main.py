import collections


class RanaNode:
    def __init__(self, node_id, neighbors):
        self.node_id = node_id
        self.neighbors = set(neighbors)
        self.active = False
        self.clock = 0
        self.wave_clock = 0
        self.parent = None
        self.expected_replies = 0
        self.in_wave = False
        self.decided = False
        self.transit_messages = []

    def send_basic(self, target):
        self.clock += 1
        self.transit_messages.append((target, 'basic', self.clock))

    def receive_basic(self, msg_clock):
        self.clock = max(self.clock, msg_clock) + 1
        self.active = True

    def become_passive(self):
        self.active = False
        self.initiate_wave()

    def initiate_wave(self):
        if not self.active and not self.in_wave:
            self.in_wave = True
            self.wave_clock = self.clock
            self.parent = self.node_id
            self.expected_replies = len(self.neighbors)
            for neighbor in self.neighbors:
                self.transit_messages.append((neighbor, 'control', self.wave_clock))
            if self.expected_replies == 0:
                if self.clock == self.wave_clock:
                    self.decided = True

    def receive_control(self, sender, wave_clock):
        if wave_clock > self.wave_clock:
            self.wave_clock = wave_clock
            self.in_wave = True
            self.parent = sender
            self.expected_replies = len(self.neighbors) - 1
            for neighbor in self.neighbors:
                if neighbor != self.parent:
                    self.transit_messages.append((neighbor, 'control', self.wave_clock))
            if self.expected_replies == 0:
                self.transit_messages.append((self.parent, 'reply', self.wave_clock))
                self.in_wave = False
        elif wave_clock == self.wave_clock:
            self.transit_messages.append((sender, 'reply', self.wave_clock))

    def receive_reply(self, wave_clock):
        if self.in_wave and wave_clock == self.wave_clock:
            self.expected_replies -= 1
            if self.expected_replies == 0:
                self.in_wave = False
                if self.parent == self.node_id:
                    if not self.active and self.clock == self.wave_clock:
                        self.decided = True
                else:
                    self.transit_messages.append((self.parent, 'reply', self.wave_clock))


class RanaSimulator:
    def __init__(self, graph):
        self.nodes = {u: RanaNode(u, neighbors) for u, neighbors in graph.items()}
        self.queue = collections.deque()

    def dispatch_basic(self, sender, target):
        self.nodes[sender].send_basic(target)
        self._flush_transit(sender)

    def become_passive(self, node_id):
        self.nodes[node_id].become_passive()
        self._flush_transit(node_id)

    def _flush_transit(self, node_id):
        node = self.nodes[node_id]
        while node.transit_messages:
            msg = node.transit_messages.pop(0)
            self.queue.append((msg[0], node_id, msg[1], msg[2] if len(msg) > 2 else None))

    def run(self):
        steps = 0
        while self.queue:
            target, sender, mtype, payload = self.queue.popleft()
            if mtype == 'basic':
                self.nodes[target].receive_basic(payload)
            elif mtype == 'control':
                self.nodes[target].receive_control(sender, payload)
            elif mtype == 'reply':
                self.nodes[target].receive_reply(payload)

            self._flush_transit(target)
            steps += 1

        decided_nodes = [n.node_id for n in self.nodes.values() if n.decided]
        return steps, decided_nodes


class SafraNode:
    def __init__(self, node_id, is_initiator=False):
        self.node_id = node_id
        self.is_initiator = is_initiator
        self.active = False
        self.color = "white"
        self.message_count = 0
        self.has_token = is_initiator
        self.token = {'color': 'white', 'q': 0} if is_initiator else None
        self.decided = False
        self.transit_messages = []

    def send_basic(self, target):
        self.message_count += 1
        self.color = "black"
        self.transit_messages.append((target, 'basic'))

    def receive_basic(self):
        self.message_count -= 1
        self.active = True

    def become_passive(self):
        self.active = False

    def process_token(self, next_node):
        if not self.active and self.has_token and not self.decided:
            if self.is_initiator:
                if self.color == "white" and self.token['color'] == "white" and self.token[
                    'q'] + self.message_count == 0:
                    self.decided = True
                    return
                self.token = {'color': 'white', 'q': 0}
                if self.color == "black":
                    self.token['color'] = "black"
                self.color = "white"
                self.transit_messages.append((next_node, 'token', self.token.copy()))
                self.has_token = False
                self.token = None
            else:
                self.token['q'] += self.message_count
                if self.color == "black":
                    self.token['color'] = "black"
                self.color = "white"
                self.transit_messages.append((next_node, 'token', self.token.copy()))
                self.has_token = False
                self.token = None

    def receive_token(self, token):
        self.has_token = True
        self.token = token


class SafraSimulator:
    def __init__(self, n):
        self.n = n
        self.nodes = {i: SafraNode(i, is_initiator=(i == 0)) for i in range(n)}
        self.queue = collections.deque()

    def dispatch_basic(self, sender, target):
        self.nodes[sender].send_basic(target)
        self._flush_transit(sender)

    def become_passive(self, node_id):
        self.nodes[node_id].become_passive()

    def _flush_transit(self, node_id):
        node = self.nodes[node_id]
        while node.transit_messages:
            msg = node.transit_messages.pop(0)
            self.queue.append((msg[0], node_id, msg[1], msg[2] if len(msg) > 2 else None))

    def run(self):
        steps = 0
        while True:
            progress = False
            if self.queue:
                target, sender, mtype, payload = self.queue.popleft()
                if mtype == 'basic':
                    self.nodes[target].receive_basic()
                elif mtype == 'token':
                    self.nodes[target].receive_token(payload)
                self._flush_transit(target)
                steps += 1
                progress = True

            for i in range(self.n):
                if self.nodes[i].has_token and not self.nodes[i].active and not self.nodes[i].decided:
                    next_node = (i + 1) % self.n
                    self.nodes[i].process_token(next_node)
                    self._flush_transit(i)
                    progress = True

            if self.nodes[0].decided:
                break
            if not progress and not self.queue:
                break
        return steps


def test_simulators():
    rana_graph = {
        1: [2, 3],
        2: [1, 3],
        3: [1, 2]
    }

    rana_sim = RanaSimulator(rana_graph)
    rana_sim.nodes[1].active = True
    rana_sim.nodes[2].active = True

    rana_sim.dispatch_basic(1, 2)
    rana_sim.dispatch_basic(2, 3)

    rana_sim.become_passive(1)
    rana_sim.become_passive(2)
    rana_sim.run()
    rana_sim.become_passive(3)
    steps_rana, rana_decided = rana_sim.run()

    print("Testing Rana's Algorithm:")
    print(f"Simulation completed in {steps_rana} control steps.")
    print(f"Nodes that detected termination: {rana_decided}\n")

    print("Testing Safra's Algorithm:")
    safra_sim = SafraSimulator(4)
    safra_sim.nodes[0].active = True
    safra_sim.nodes[1].active = True

    safra_sim.dispatch_basic(0, 1)
    safra_sim.dispatch_basic(1, 2)

    safra_sim.become_passive(0)
    safra_sim.become_passive(1)
    safra_sim.run()

    safra_sim.become_passive(2)
    steps_safra = safra_sim.run()

    print(f"Simulation completed in {steps_safra} steps.")
    print(f"Initiator (Node 0) detected termination: {safra_sim.nodes[0].decided}")


if __name__ == "__main__":
    test_simulators()