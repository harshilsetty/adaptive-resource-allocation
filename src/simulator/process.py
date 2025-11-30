import time
import random

class SimulatedProcess:
    def __init__(self, pid, kind, cpu_demand=1, mem_demand_mb=10):
        self.pid = pid            # unique ID
        self.kind = kind          # cpu / io / mem
        self.cpu_demand = cpu_demand
        self.mem_demand_mb = mem_demand_mb

        self.total_cpu_time = 0.0
        self.wait_time = 0.0
        self.completed = False

    def run_for(self, duration_seconds):
        """Simulate running this process for a time slice."""
        start = time.time()

        if self.kind == "cpu":
            # CPU-bound: busy loop
            end = start + duration_seconds
            while time.time() < end:
                _ = random.random() * random.random()
            used = duration_seconds

        elif self.kind == "io":
            # I/O bound: mostly waits
            time.sleep(duration_seconds * 0.7)
            used = duration_seconds * 0.3

        elif self.kind == "mem":
            # Memory-heavy process
            arr = [0] * (self.mem_demand_mb * 200)
            time.sleep(duration_seconds * 0.1)
            used = duration_seconds * 0.9
            del arr

        else:
            used = duration_seconds

        self.total_cpu_time += used
        return used
