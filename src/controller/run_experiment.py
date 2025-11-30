import argparse
import json
import time

from simulator.process import SimulatedProcess
from simulator.scheduler_rr import RoundRobinScheduler
from monitor.monitor import Monitor
from allocator.heuristic_allocator import HeuristicAllocator

def load_workload(path):
    with open(path, "r") as f:
        return json.load(f)

def create_processes(workload):
    processes = []
    pid = 1

    for _ in range(workload.get("cpu_bound", 0)):
        processes.append(SimulatedProcess(pid, "cpu"))
        pid += 1

    for _ in range(workload.get("io_bound", 0)):
        processes.append(SimulatedProcess(pid, "io"))
        pid += 1

    for _ in range(workload.get("mem_bound", 0)):
        processes.append(SimulatedProcess(pid, "mem"))
        pid += 1

    return processes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload", default="workloads/mix1.json")
    parser.add_argument("--duration", default=10, type=int)
    args = parser.parse_args()

    workload = load_workload(args.workload)
    processes = create_processes(workload)

    monitor = Monitor(sample_interval=0.2)
    allocator = HeuristicAllocator(processes)
    scheduler = RoundRobinScheduler(processes, slice_sec=0.05)

    start = time.time()

    while time.time() - start < args.duration:
        pid, used = scheduler.step()
        monitor.sample(processes)
        allocator.update(monitor.history)

    print("\nFinal Adaptive Weights:")
    print(allocator.get_weights())

if __name__ == "__main__":
    main()
