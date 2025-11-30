class HeuristicAllocator:
    def __init__(self, processes):
        # Each process starts with weight = 1
        self.weights = {p.pid: 1 for p in processes}

    def update(self, history):
        """Update weights based on recent CPU usage."""
        for pid, samples in history.items():
            if len(samples) < 2:
                continue
            
            last = samples[-1]
            prev = samples[-2]

            cpu_delta = last["total_cpu"] - prev["total_cpu"]

            # Simple adaptive rules:
            if cpu_delta < 0.01:
                # Not getting enough CPU → increase weight
                self.weights[pid] += 1
            elif cpu_delta > 0.1:
                # Getting too much CPU → reduce weight slightly
                self.weights[pid] = max(1, self.weights[pid] - 1)

    def get_weights(self):
        return self.weights
