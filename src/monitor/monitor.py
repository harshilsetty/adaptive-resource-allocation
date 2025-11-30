import time
from collections import defaultdict

class Monitor:
    def __init__(self, sample_interval=0.2):
        self.sample_interval = sample_interval
        self.history = defaultdict(list)

    def sample(self, processes):
        timestamp = time.time()

        for p in processes:
            self.history[p.pid].append({
                "t": timestamp,
                "total_cpu": p.total_cpu_time,
                "wait_time": p.wait_time,
                "kind": p.kind
            })

        time.sleep(self.sample_interval)
