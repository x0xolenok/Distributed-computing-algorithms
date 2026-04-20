class LamportClock:
    def __init__(self, process_id):
        self.process_id = process_id
        self.time = 0

    def local_event(self):
        self.time += 1
        return self.time

    def send_event(self):
        self.time += 1
        return self.time

    def receive_event(self, received_time):
        self.time = max(self.time, received_time) + 1
        return self.time


class VectorClock:
    def __init__(self, num_processes, process_id):
        self.process_id = process_id
        self.clock = [0] * num_processes

    def local_event(self):
        self.clock[self.process_id] += 1
        return list(self.clock)

    def send_event(self):
        self.clock[self.process_id] += 1
        return list(self.clock)

    def receive_event(self, received_clock):
        self.clock[self.process_id] += 1
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], received_clock[i])
        return list(self.clock)


if __name__ == "__main__":

    # LAMPORT CLOCK DEMONSTRATION

    print(" Lamport Clock Simulation")

    # Initialize Lamport clocks for 2 processes
    p0 = LamportClock(0)
    p1 = LamportClock(1)

    # Process 0 performs a local event
    t1 = p0.local_event()
    print(f"P0 local event          -> Time: {t1}")

    # Process 0 prepares to send a message to Process 1
    t2 = p0.send_event()
    print(f"P0 sends message        -> Time: {t2}")

    # Process 1 performs its own local event before receiving
    t_p1 = p1.local_event()
    print(f"P1 local event          -> Time: {t_p1}")

    # Process 1 receives the message from Process 0
    t3 = p1.receive_event(t2)
    print(f"P1 receives message     -> Time: {t3}\n")


    # VECTOR CLOCK DEMONSTRATION

    print(" Vector Clock Simulation ")

    # Initialize Vector clocks for 3 processes
    vp0 = VectorClock(num_processes=3, process_id=0)
    vp1 = VectorClock(num_processes=3, process_id=1)
    vp2 = VectorClock(num_processes=3, process_id=2)

    # Process 0 performs a local event
    v1 = vp0.local_event()
    print(f"P0 local event          -> Vector: {v1}")

    # Process 0 sends a message to Process 1
    v2 = vp0.send_event()
    print(f"P0 sends message to P1  -> Vector: {v2}")

    # Process 1 receives the message from Process 0
    v3 = vp1.receive_event(v2)
    print(f"P1 receives from P0     -> Vector: {v3}")

    # Process 1 performs a local event
    v4 = vp1.local_event()
    print(f"P1 local event          -> Vector: {v4}")

    # Process 1 sends a message to Process 2
    v5 = vp1.send_event()
    print(f"P1 sends message to P2  -> Vector: {v5}")

    # Process 2 receives the message from Process 1
    v6 = vp2.receive_event(v5)
    print(f"P2 receives from P1     -> Vector: {v6}")