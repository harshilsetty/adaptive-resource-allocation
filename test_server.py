from flask import Flask, request, jsonify
from flask_cors import CORS
import importlib.util
import os
import traceback

app = Flask(__name__)
CORS(app)

# Try dynamic import of resource_allocation.py (the file with new functions)
ALLOCATOR_FN = None
mod = None
try:
    path = os.path.join(os.getcwd(), "resource_allocation.py")
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location("resource_allocation", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Prefer allocate_respecting_capacities if present
        if hasattr(mod, "allocate_respecting_capacities"):
            ALLOCATOR_FN = mod.allocate_respecting_capacities
        elif hasattr(mod, "adaptive_allocate_fixed"):
            ALLOCATOR_FN = mod.adaptive_allocate_fixed
        # else ALLOCATOR_FN remains None
except Exception:
    print("Import error while loading resource_allocation.py:")
    traceback.print_exc()
    ALLOCATOR_FN = None
    mod = None


@app.route("/allocate", methods=["POST"])
def allocate_route():
    data = request.get_json() or {}
    capacities = data.get("capacities") or data.get("capacities_list") or []
    demands = data.get("demands") or data.get("demands_list") or []
    # Accept algorithm param (ignore if backend doesn't support)
    algorithm = data.get("algorithm")

    # Normalize numeric inputs (defensive)
    try:
        capacities = [float(c) for c in capacities]
    except Exception:
        capacities = []
    try:
        demands = [float(d) for d in demands]
    except Exception:
        demands = []

    # If allocator function is available, call it
    if ALLOCATOR_FN:
        try:
            if ALLOCATOR_FN.__name__ == "allocate_respecting_capacities":
                result = ALLOCATOR_FN(capacities, demands)
            else:
                # adaptive_allocate_fixed expects Task/Resource objects; build them
                # ensure mod is available
                if mod is None:
                    raise RuntimeError("Allocator module not available")
                tasks_obj = [mod.Task(f"T{i+1}", d) for i, d in enumerate(demands)]
                resources_obj = [mod.Resource(f"R{i+1}", c) for i, c in enumerate(capacities)]
                result = ALLOCATOR_FN(tasks_obj, resources_obj)
            # result should already be a JSON-serializable dict with keys:
            # "status", "allocations" (flattened), "resource_status", "unallocated"
            return jsonify(result)
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({"status": "error", "message": f"allocator error: {e}", "trace": tb}), 500

    # Fallback naive behavior (old dummy), if ALLOCATOR_FN wasn't loaded
    flattened = []
    for i, d in enumerate(demands, start=1):
        if not capacities:
            flattened.append({"task": i, "resource": "R1", "allocated": d})
        else:
            ri = (i - 1) % len(capacities)
            amt = min(d, capacities[ri])
            flattened.append({"task": i, "resource": f"R{ri+1}", "allocated": amt})

    # compute resource_status
    used = [0.0] * len(capacities)
    for a in flattened:
        # guard: ignore non-standard resources
        rname = a.get("resource", "")
        if str(rname).startswith("R"):
            try:
                ridx = int(str(rname).lstrip("R")) - 1
                if 0 <= ridx < len(used):
                    used[ridx] += float(a.get("allocated", 0))
            except Exception:
                pass

    resource_status = []
    for idx, cap in enumerate(capacities):
        resource_status.append({
            "resource": f"R{idx+1}",
            "used": used[idx],
            "capacity": float(cap),
            "remaining": float(cap) - used[idx]
        })

    return jsonify({"status": "success", "allocations": flattened, "resource_status": resource_status, "unallocated": []})


if __name__ == "__main__":
    print("Starting test_server.py")
    print(" - Listening on http://127.0.0.1:5000")
    print(" - Make POST requests to /allocate")
    try:
        # debug=True to show stack traces in server console; remove in production
        app.run(host="127.0.0.1", port=5000, debug=True)
    except Exception:
        print("Failed to start Flask server:")
        traceback.print_exc()
