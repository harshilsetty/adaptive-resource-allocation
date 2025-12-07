import sys
import os
import pandas as pd
from datetime import datetime

def jain_index(values):
    if not values or sum(values) == 0:
        return 0.0
    s = sum(values)
    s2 = sum(v*v for v in values)
    n = len(values)
    return (s*s) / (n * s2)

if len(sys.argv) < 2:
    print("Usage: python scripts/summarize_results.py <csv-file>")
    sys.exit(1)

csv_file = sys.argv[1]
df = pd.read_csv(csv_file)

last_samples = df.sort_values(["sample_idx"]).groupby("pid").tail(1)

totals = last_samples.set_index("pid")["total_cpu"].to_dict()

summary_rows = []
total_cpu_all = sum(totals.values())
for pid, tot in totals.items():
    summary_rows.append({
        "pid": int(pid),
        "total_cpu": float(tot),
        "cpu_share": float(tot) / total_cpu_all if total_cpu_all > 0 else 0.0
    })

summary_df = pd.DataFrame(summary_rows).sort_values("pid")

fairness = jain_index(summary_df["total_cpu"].tolist())

print("\n=== Summary (last sample per pid) ===")
print(summary_df.to_string(index=False))
print(f"\nTotal CPU Time = {total_cpu_all:.4f} seconds")
print(f"Jain Fairness Index = {fairness:.4f}")

out_path = f"results/summary_{os.path.basename(csv_file).replace('.csv','')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
summary_df.to_csv(out_path, index=False)
print("\nSummary CSV saved to:", out_path)
