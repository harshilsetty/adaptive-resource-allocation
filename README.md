# Adaptive Resource Allocation System  
CSE316 Mini Project — Final Implementation  
Author: **Harshil Somisetty**

---

## 1. Overview
This project implements an **Adaptive Resource Allocation System** that assigns tasks to resources based on given capacities and demands.

It includes:

- A **Flask backend API** (`/allocate`)
- A fully functional **frontend UI** (`frontend/`)
- Results table, usage summary, bar charts, and CSV export
- Auto-filled values for fast demo
- LocalStorage support for persistence

The system is designed to be simple, fast, and ideal for viva/demo presentation.

---

## 2. Folder Structure
```
adaptive-resource-allocation/
├─ frontend/
│  ├─ index.html
│  ├─ style.css
│  ├─ app.js
│  └─ assets/
├─ resource_allocation.py
├─ test_server.py
├─ requirements.txt
├─ docs/
├─ src/
└─ workloads/
```

---

## 3. How to Run the Project (Local Demo)

### Step 1 — Open project folder
```powershell
cd "C:\Users\HARSHIL SOMISETTY\Desktop\adaptive-resource-allocation"
```

### Step 2 — Activate virtual environment  
If venv exists:
```powershell
.\venv\Scripts\Activate
```

If not, create new:
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### Step 3 — Start backend server
```powershell
python test_server.py
```

Output should include:
```
Running on http://127.0.0.1:5000
```

### Step 4 — Open frontend
Open:
```
frontend/index.html
```

The page auto-fills:
- Capacities: `10,8,12`
- Demands: `4,6,11,8`

Click **Run Allocation** to view results.

---

## 4. API Reference

### Endpoint
```
POST /allocate
```

### Sample Request
```json
{
  "num_resources": 3,
  "capacities": [10, 8, 12],
  "num_tasks": 4,
  "demands": [4, 6, 11, 8],
  "algorithm": "round_robin"
}
```

### Sample Response
```json
{
  "status": "success",
  "allocations": [
    {"task": 1, "resource": "R1", "allocated": 4},
    {"task": 2, "resource": "R2", "allocated": 6},
    {"task": 3, "resource": "R3", "allocated": 11},
    {"task": 4, "resource": "R1", "allocated": 8}
  ],
  "resource_status": [
    {"resource": "R1", "used": 12, "capacity": 10, "remaining": -2},
    {"resource": "R2", "used": 6, "capacity": 8, "remaining": 2},
    {"resource": "R3", "used": 11, "capacity": 12, "remaining": 1}
  ],
  "unallocated": []
}
```

---

## 5. Features

### Backend
- Flask API for processing allocations
- Automatically loads logic from `resource_allocation.py`
- Clean error handling and JSON responses

### Frontend
- Modern UI (HTML + CSS + JS)
- Auto-filled example values
- Validations for invalid inputs
- Allocation results table
- Remaining capacity summary
- Bar chart (Chart.js)
- CSV export
- Persistent inputs (localStorage)

---

## 6. Viva Demo Script (60–90 seconds)

1. This is the Adaptive Resource Allocation System developed for CSE316.  
2. The backend uses Flask and exposes a POST endpoint at `/allocate`.  
3. The frontend takes user inputs, sends them to the backend, and displays results in a table and bar chart.  
4. When I click Run Allocation, the backend processes the request and returns the mapping of tasks to resources.  
5. The UI also shows remaining capacities and overloads.  
6. The system supports CSV export, auto-filled values, and persistent inputs.  
7. This project is modular and allows easy extension of allocation strategies.

---

## 7. Troubleshooting

### Browser says “connection refused”
Backend not running. Start:
```powershell
python test_server.py
```

### No chart visible
Check internet (Chart.js CDN).

### Wrong allocations
Check logic inside:
```
resource_allocation.py
```

---

## 8. Optional — Host Frontend on GitHub Pages
To host only the static UI:
```bash
git subtree push --prefix frontend origin gh-pages
```

Page will be available at:
```
https://harshilsetty.github.io/adaptive-resource-allocation/
```

---

## 9. License
Created as part of the CSE316 course.  
Free to reuse for learning and portfolio purposes.

