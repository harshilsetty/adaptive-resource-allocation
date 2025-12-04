# Adaptive Resource Allocation in Multiprogramming Systems  
CSE316 — Operating Systems  
CA2 Project • Lovely Professional University  

---

## 📌 Project Overview
This project simulates a multiprogramming environment where multiple processes (CPU-bound, I/O-bound, and memory-intensive) compete for CPU time.  
An **Adaptive CPU Allocator** dynamically adjusts scheduling weights for each process based on real-time CPU utilization trends.  
The system compares:
- **Round-Robin (Baseline Scheduler)**
- **Adaptive Scheduling (Heuristic-based)**

The project includes full logging, plotting, and fairness evaluation using **Jain's Fairness Index**.

---

## 🧩 Modules Implemented
### 1️⃣ Simulator  
- Implements CPU, I/O, and memory-bound process behavior  
- Round-Robin scheduler with time slices  
- Tracks CPU time, wait time, and execution history  

### 2️⃣ Monitor  
- Periodically samples process CPU time and wait time  
- Stores historical data for analysis  
- Basis for allocator decision-making  

### 3️⃣ Adaptive Allocator  
- Computes CPU allocation weights using CPU delta  
- Includes basic + aggressive heuristic versions  
- Dynamically updates weights for fairness and efficiency  

### 4️⃣ Controller / Experiment Runner  
- Runs full experiments end-to-end  
- Integrates simulator + monitor + allocator  
- Logs results into CSV format  

### 5️⃣ Plotting & Summary Tools  
- Graphs CPU usage over time  
- Graphs weight updates over time  
- Computes fairness metrics  
- Summarizes CPU usage distribution  

---

## 📁 Project Structure
```
adaptive-resource-allocation/
│
├── src/
│   ├── simulator/
│   ├── monitor/
│   ├── allocator/
│   └── controller/
│
├── scripts/
│   ├── plot_results.py
│   └── summarize_results.py
│
├── workloads/
│   └── mix1.json
│
├── results/
│   └── (CSV logs and plots generated here)
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 How to Run the Project

### 1️⃣ Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3️⃣ Run Adaptive Scheduler
```powershell
python src/controller/run_experiment.py --workload workloads/mix1.json --duration 10 --policy adaptive
```

### 4️⃣ Run Round Robin Baseline
```powershell
python src/controller/run_baseline_rr.py --workload workloads/mix1.json --duration 10
```

### 5️⃣ Plot Results
```powershell
python scripts/plot_results.py results/<your_csv_file>.csv
```

### 6️⃣ Summarize Results
```powershell
python scripts/summarize_results.py results/<your_csv_file>.csv
```

---

## 📊 Output Examples
The project automatically generates:
- `cpu_over_time.png`  
- `weights_over_time.png`  
- CSV logs inside `results/`  
- Summary CSV with total CPU per PID & Jain fairness  

These outputs are used in the CA2 report.

---

## 🔗 GitHub Repository
**Repository Name:** adaptive-resource-allocation  
**GitHub Link:** https://github.com/harshilsetty/adaptive-resource-allocation  

---

## 📝 Academic Notes
This project is completed as part of **CSE316 — Operating Systems CA2**, following all guidelines:
- AI-guided project breakdown  
- Modular implementation  
- GitHub revision tracking (7+ commits)  
- Evaluation using RR vs Adaptive  
- Report-ready outputs  

---

## 👨‍💻 Author
**Harshil Somisetty**  
B.Tech CSE, Lovely Professional University  
