from .process import SimulatedProcess



class RoundRobinScheduler:
    def __init__(self, processes, slice_sec=0.05):
        self.processes = processes
        self.slice = slice_sec
        self.index = 0

    def step(self):
        """Run one scheduling step."""
        p = self.processes[self.index]

        used = p.run_for(self.slice)

        # Move to next
        self.index = (self.index + 1) % len(self.processes)

        return p.pid, used
