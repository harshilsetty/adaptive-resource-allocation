# src/allocator/heuristic_allocator.py
# More aggressive heuristic for short experiments (60s)
class HeuristicAllocator:
    def __init__(self, processes, min_w=1, max_w=100):
        # Start with weight 10 to allow noticeable differentiation
        self.weights = {p.pid: 10 for p in processes}
        self.min_w = min_w
        self.max_w = max_w
        # smoothing memory
        self.prev_cpu = {}

    def update(self, history):
        """
        history: dict pid -> list of samples (each sample has 'total_cpu' and 'time')
        Heuristic:
          - compute recent CPU delta per sample window
          - if delta is very small -> increase weight by +5 (give more CPU)
          - if delta is large -> reduce weight proportional to delta
          - clamp weights to [min_w, max_w]
        """
        for pid, samples in history.items():
            if len(samples) < 2:
                continue
            last = samples[-1]
            prev = samples[-2]
            cpu_delta = last["total_cpu"] - prev["total_cpu"]

            # smoothing with previous observed delta
            prev_delta = self.prev_cpu.get(pid, cpu_delta)
            smoothed = 0.6 * prev_delta + 0.4 * cpu_delta
            self.prev_cpu[pid] = smoothed

            # aggressive reaction thresholds
            if smoothed < 0.02:
                # not consuming -> big bump
                self.weights[pid] = min(self.max_w, self.weights.get(pid,10) + 5)
            elif smoothed > 0.5:
                # extremely CPU heavy -> reduce more
                dec = int(smoothed * 5)
                self.weights[pid] = max(self.min_w, self.weights.get(pid,10) - dec)
            elif smoothed > 0.2:
                # moderately heavy
                self.weights[pid] = max(self.min_w, self.weights.get(pid,10) - 2)
            else:
                # small adjustments to encourage fairness
                # if currently high weight but using little CPU, keep it
                pass

    def get_weights(self):
        return self.weights
