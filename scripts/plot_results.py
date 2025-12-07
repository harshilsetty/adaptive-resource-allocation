# scripts/plot_results.py
# Usage: python scripts/plot_results.py results/run_adaptive_mix1_2025...csv
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print("Usage: python scripts/plot_results.py <csv-file>")
    sys.exit(1)

csv_file = sys.argv[1]
df = pd.read_csv(csv_file)

# pivot CPU over time per pid
df['time_rel'] = df['sample_idx']  # sample index as x-axis
cpu_pivot = df.pivot(index='time_rel', columns='pid', values='total_cpu')
weight_pivot = df.pivot(index='time_rel', columns='pid', values='weight')

os.makedirs("results/plots", exist_ok=True)

# Plot total_cpu progression per pid
plt.figure(figsize=(10,5))
for col in cpu_pivot.columns:
    plt.plot(cpu_pivot.index, cpu_pivot[col], label=f"pid{col}")
plt.xlabel("sample_idx")
plt.ylabel("total_cpu_time (s)")
plt.title("Total CPU time per PID over samples")
plt.legend()
plt.tight_layout()
cpu_png = os.path.join("results/plots", "cpu_over_time.png")
plt.savefig(cpu_png)
plt.close()
print("Saved:", cpu_png)

# Plot weights per pid over time
plt.figure(figsize=(10,5))
for col in weight_pivot.columns:
    plt.plot(weight_pivot.index, weight_pivot[col], label=f"pid{col}")
plt.xlabel("sample_idx")
plt.ylabel("weight")
plt.title("Allocator Weights per PID over samples")
plt.legend()
plt.tight_layout()
weights_png = os.path.join("results/plots", "weights_over_time.png")
plt.savefig(weights_png)
plt.close()
print("Saved:", weights_png)
