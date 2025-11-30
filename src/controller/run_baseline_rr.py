# src/controller/run_baseline_rr.py
# Simple RR baseline runner that logs CSV similarly to adaptive run (but no allocator updates)

import sys
import os
import argparse
import json
import time
from datetime import datetime
import csv

# ensure imports work
this_dir = os.path.abspath(os.path.dirname(__file__))
project_src = os.path.abspath(os.path.join(this_dir, ".."))
if project_src not in sys.path:
    sys.path.insert(0, project_src)

from simulator.process import SimulatedProcess
from simulator.scheduler_rr import RoundRobinScheduler
from monitor.monitor import Monitor

def load_workload(path):
    with open(path, "r") as f:
        return json.load(f)

def create_processes(workload):
    processes = []
    pid = 1
    for _ in range(workload.get("cpu_bound", 0)):
        processes.append(SimulatedProcess(pid, "cpu")); pid += 1
    for _ in range(workload.get("io_bound", 0)):
        processes.append(SimulatedProcess(pid, "io")); pid += 1
    for _ in range(workload.get("mem_bound", 0)):
        processes.append(SimulatedProcess(pid, "mem")); pid += 1
    return processes

def save_csv(rows, filename):
    if not rows:
        return
    keys = list(rows[0].keys())
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload", default="workloads/mix1.json")
    parser.add_argument("--duration", default=10, type=int)
    parser.add_argument("--slice", default=0.05, type=float)
    parser.add_argument("--sample-interval", default=0.2, type=float)
    args = parser.parse_args()

    workload = load_workload(args.workload)
    processes = create_processes(workload)

    monitor = Monitor(sample_interval=args.sample_interval)
    scheduler = RoundRobinScheduler(processes, slice_sec=args.slice)

    rows = []
    start_time = time.time()
    sample_idx = 0
    print(f"Starting RR baseline: duration={args.duration}s, processes={len(processes)}")
    while time.time() - start_time < args.duration:
        pid, used = scheduler.step()
        monitor.sample(processes)  # collects history, sleeps sample_interval

        # No allocator -> weight=1 always
        timestamp = time.time()
        for p in processes:
            row = {
                "sample_idx": sample_idx,
                "time": timestamp,
                "pid": p.pid,
                "kind": p.kind,
                "total_cpu": p.total_cpu_time,
                "wait_time": p.wait_time,
                "weight": 1
            }
            rows.append(row)
        sample_idx += 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workload_name = os.path.splitext(os.path.basename(args.workload))[0]
    csv_path = f"results/run_rr_{workload_name}_{stamp}.csv"
    save_csv(rows, csv_path)
    print("Done. CSV saved to:", csv_path)

if __name__ == "__main__":
    main()
