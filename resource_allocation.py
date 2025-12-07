# Adaptive Resource Allocation System
# CSE316 Mini Project Implementation

class Resource:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = float(capacity)
        self.used = 0.0

    def allocate(self, amount):
        # allocate up to remaining capacity, return actual allocated
        available = max(0.0, self.capacity - self.used)
        take = min(available, float(amount))
        if take > 0:
            self.used += take
        return take

    def remaining(self):
        return max(0.0, self.capacity - self.used)

    def __str__(self):
        return f"{self.name}: {int(self.used)}/{int(self.capacity)} used" if int(self.used)==self.used else f"{self.name}: {self.used}/{self.capacity} used"


class Task:
    def __init__(self, name, demand):
        self.name = name
        self.demand = float(demand)


def allocate_respecting_capacities(capacities, demands):
    """
    capacities: list of numbers (resource capacities)
    demands: list of numbers (task demands)

    Returns:
      {
        "status": "success",
        "allocations": [ {"task": 1, "resource": "R1", "allocated": 5}, ... ],
        "resource_status": [ {"resource":"R1","used":5,"capacity":10,"remaining":5}, ... ],
        "unallocated": [ {"task": 3, "remaining": 2.5}, ... ]  # optional
      }

    Behavior:
      - Fills each task by consuming remaining capacity of resources in order R1..Rn.
      - Never allocates more than remaining capacity.
      - If task can't be fully satisfied, leftover marked in "unallocated".
    """
    # defensive copy of capacities
    remaining = [float(c) for c in capacities]
    flattened = []
    unallocated = []

    for ti, demand in enumerate(demands, start=1):
        req = float(demand)
        for ri in range(len(remaining)):
            if req <= 0:
                break
            if remaining[ri] <= 0:
                continue
            take = min(remaining[ri], req)
            if take > 0:
                remaining[ri] -= take
                req -= take
                flattened.append({
                    "task": ti,
                    "resource": f"R{ri+1}",
                    "allocated": take
                })
        if req > 0:
            unallocated.append({"task": ti, "remaining": req})

    resource_status = []
    for ri, cap in enumerate(capacities):
        used = float(cap) - remaining[ri]
        resource_status.append({
            "resource": f"R{ri+1}",
            "used": used,
            "capacity": float(cap),
            "remaining": remaining[ri]
        })

    return {
        "status": "success",
        "allocations": flattened,
        "resource_status": resource_status,
        "unallocated": unallocated
    }


def adaptive_allocate_fixed(tasks, resources):
    """
    Backwards-compatible wrapper that works with your Resource and Task classes.
    This will try to allocate each task by consuming resource remaining capacities
    in order, splitting across resources if needed (but never exceeding capacity).
    Returns the same structured dict as allocate_respecting_capacities.
    """
    # extract numeric lists, but keep the Resource objects to update their 'used'
    caps = [r.capacity for r in resources]

    # Use allocate_respecting_capacities to get allocation plan
    demands = [t.demand for t in tasks]
    plan = allocate_respecting_capacities(caps, demands)

    # Apply the flattened allocations back to the Resource objects (update used)
    # This keeps your in-memory Resource.used consistent if you want to print later
    # Note: plan['allocations'] contains resource names like "R1"
    for a in plan["allocations"]:
        res_index = int(a["resource"].lstrip("R")) - 1
        # allocate amount (this uses Resource.allocate which caps safely)
        resources[res_index].allocate(a["allocated"])

    return plan


# ------------------ EXAMPLE USAGE (keep or remove in integration) ------------------
if __name__ == "__main__":
    # sample resources/tasks (same as your original)
    resources = [
        Resource("Resource A", 10),
        Resource("Resource B", 8),
        Resource("Resource C", 12)
    ]

    tasks = [
        Task("Task 1", 4),
        Task("Task 2", 6),
        Task("Task 3", 3),
        Task("Task 4", 8)
    ]

    result = adaptive_allocate_fixed(tasks, resources)

    # flatten result for pretty printing
    print("=== Adaptive Resource Allocation Result ===")
    # group allocations by task for human readable output
    from collections import defaultdict
    by_task = defaultdict(list)
    for a in result["allocations"]:
        by_task[a["task"]].append((a["resource"], a["allocated"]))

    for t_idx, t in enumerate(tasks, start=1):
        allocs = by_task.get(t_idx, [])
        if not allocs:
            print(f"{t.name} → Not Allocated (remaining demand: {next((u['remaining'] for u in result['unallocated'] if u['task']==t_idx), 0)})")
        else:
            # show combined resources for this task
            parts = ", ".join([f"{res} ({int(val) if val==int(val) else val})" for res, val in allocs])
            print(f"{t.name} → {parts}")

    print("\nResource Status:")
    for rs in result["resource_status"]:
        used = int(rs["used"]) if rs["used"] == int(rs["used"]) else rs["used"]
        cap = int(rs["capacity"]) if rs["capacity"] == int(rs["capacity"]) else rs["capacity"]
        rem = int(rs["remaining"]) if rs["remaining"] == int(rs["remaining"]) else rs["remaining"]
        print(f"{rs['resource']}: {used}/{cap} used — remaining {rem}")
