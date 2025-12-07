// app.js – Frontend logic with chart, algorithm selection, theme toggle

const API_URL = "http://127.0.0.1:5000/allocate";

const el = id => document.getElementById(id);
const runBtn = el("runBtn");
const clearBtn = el("clearBtn");
const exportBtn = el("exportBtn");
const spinner = el("spinner");
const message = el("message");
const resultsContainer = el("resultsContainer");
const capacityContainer = el("capacityContainer");
const capacityList = el("capacityList");
const algorithmSelect = el("algorithm");
const themeToggle = el("themeToggle");
const chartCard = el("chartCard");
const allocChartCanvas = el("allocChart");

let allocChart = null;

function showSpinner(state = true) {
    spinner.style.display = state ? "inline-block" : "none";
}

function showMessage(text, type = "info") {
    message.textContent = text;
    message.style.color =
        type === "error"
            ? "var(--danger)"
            : type === "success"
            ? "var(--success)"
            : "var(--muted)";
}

function parseCommaNumbers(str) {
    if (!str) return [];
    return str.split(/[\s,]+/).map(Number).filter(n => !isNaN(n));
}

function validateInputs(nR, caps, nT, demands) {
    if (nR <= 0) return "Number of resources must be > 0";
    if (caps.length !== nR) return `Capacities count (${caps.length}) must equal number of resources (${nR})`;
    if (nT <= 0) return "Number of tasks must be > 0";
    if (demands.length !== nT) return `Demands count (${demands.length}) must equal number of tasks (${nT})`;
    return null;
}

function renderResults(data) {
    resultsContainer.innerHTML = "";
    exportBtn.style.display = "none";
    capacityContainer.style.display = "none";
    capacityList.innerHTML = "";
    chartCard.style.display = "none";

    if (!data || data.status !== "success") {
        resultsContainer.innerHTML =
            `<p class="muted">Backend error: ${data?.message || "Unknown error"}</p>`;
        return;
    }

    const allocations = data.allocations || [];
    if (allocations.length === 0) {
        resultsContainer.innerHTML = '<p class="muted">No allocation results.</p>';
        return;
    }

    // build table
    let html = `
        <table class="table zebra">
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Resource</th>
                    <th>Allocated</th>
                </tr>
            </thead>
            <tbody>
    `;

    allocations.forEach(a => {
        const task = a.task ?? a.task_id ?? a.t ?? "-";
        const resource = a.resource ?? a.allocated_resource ?? a.r ?? "-";
        const allocated = a.allocated ?? a.amount ?? a.value ?? "-";
        html += `
            <tr>
                <td>${task}</td>
                <td>${resource}</td>
                <td>${allocated}</td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    resultsContainer.innerHTML = html;

    // show export button
    exportBtn.style.display = "inline-block";
    exportBtn.onclick = () => downloadCSV(allocations);

    // compute remaining capacities and show
    // ===== resource status display: prefer backend's authoritative value =====
    try {
        // use backend-provided resource_status if available (authoritative)
        if (data.resource_status && Array.isArray(data.resource_status) && data.resource_status.length) {
            let listHtml = "<ul style='margin:0;padding-left:18px;'>";
            data.resource_status.forEach(rs => {
                const used = (rs.used !== undefined) ? rs.used : "-";
                const cap = (rs.capacity !== undefined) ? rs.capacity : "-";
                const rem = (rs.remaining !== undefined) ? rs.remaining : (typeof cap === "number" && typeof used === "number" ? cap - used : "-");
                if (typeof rem === "number" && rem < 0) {
                    listHtml += `<li>Resource ${rs.resource}: ${used}/${cap} used — <strong style="color:var(--danger)">overloaded by ${Math.abs(rem)}</strong></li>`;
                } else {
                    listHtml += `<li>Resource ${rs.resource}: ${used}/${cap} used — remaining ${rem}</li>`;
                }
            });
            listHtml += "</ul>";
            capacityList.innerHTML = listHtml;
            capacityContainer.style.display = "block";
        } else {
            // fallback to local inference (existing behaviour)
            const numResources = Number(el("numResources").value);
            const capacities = parseCommaNumbers(el("capacities").value);
            const used = new Array(capacities.length).fill(0);
            (data.allocations || []).forEach(a => {
                const resName = (a.resource ?? a.allocated_resource ?? "").toString();
                const match = resName.match(/R(\d+)/i);
                if (match) {
                    const idx = Number(match[1]) - 1;
                    if (!Number.isNaN(idx) && idx >= 0 && idx < used.length) {
                        used[idx] += Number(a.allocated ?? a.amount ?? 0);
                    }
                }
            });
            let listHtml = "<ul style='margin:0;padding-left:18px;'>";
            for (let i = 0; i < capacities.length; i++) {
                const rem = capacities[i] - (used[i] || 0);
                if (rem < 0) {
                    listHtml += `<li>Resource R${i+1}: ${(used[i]||0)}/${capacities[i]} used — <strong style="color:var(--danger)">overloaded by ${Math.abs(rem)}</strong></li>`;
                } else {
                    listHtml += `<li>Resource R${i+1}: ${(used[i]||0)}/${capacities[i]} used — remaining ${rem}</li>`;
                }
            }
            listHtml += "</ul>";
            capacityList.innerHTML = listHtml;
            capacityContainer.style.display = "block";
        }
    } catch (e) {
        console.warn("resource status render error", e);
    }

    // prepare chart data (group by resource name)
    const resourceMap = {};
    allocations.forEach(a => {
        const resName = (a.resource ?? a.allocated_resource ?? "").toString() || "Unknown";
        const allocated = Number(a.allocated ?? a.amount ?? 0) || 0;
        resourceMap[resName] = (resourceMap[resName] || 0) + allocated;
    });

    const labels = Object.keys(resourceMap);
    const values = labels.map(l => resourceMap[l]);

    // draw chart
    drawChart(labels, values);
}

function downloadCSV(allocations) {
    if (!allocations || !allocations.length) return;
    const rows = [["task","resource","allocated"]];
    allocations.forEach(a => {
        const task = a.task ?? a.task_id ?? a.t ?? "";
        const resource = a.resource ?? a.allocated_resource ?? a.r ?? "";
        const allocated = a.allocated ?? a.amount ?? a.value ?? "";
        rows.push([task, resource, allocated]);
    });
    const csv = rows.map(r => r.map(cell => `"${String(cell).replace(/"/g,'""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "allocations.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}

function drawChart(labels, values) {
    chartCard.style.display = "block";
    if (allocChart) {
        allocChart.data.labels = labels;
        allocChart.data.datasets[0].data = values;
        allocChart.update();
        return;
    }

    const ctx = allocChartCanvas.getContext("2d");
    allocChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Allocated amount",
                data: values,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

async function runAllocation() {
    const numResources = Number(el("numResources").value);
    const capacities = parseCommaNumbers(el("capacities").value);
    const numTasks = Number(el("numTasks").value);
    const demands = parseCommaNumbers(el("demands").value);
    const algorithm = algorithmSelect.value;

    const error = validateInputs(numResources, capacities, numTasks, demands);
    if (error) {
        showMessage(error, "error");
        return;
    }

    const payload = {
        num_resources: numResources,
        capacities: capacities,
        num_tasks: numTasks,
        demands: demands,
        algorithm: algorithm
    };

    showSpinner(true);
    showMessage("Processing...", "info");
    resultsContainer.innerHTML = "";

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const txt = await res.text();
            throw new Error(`HTTP ${res.status}: ${txt}`);
        }

        const data = await res.json();
        showSpinner(false);
        showMessage("Success!", "success");
        renderResults(data);

    } catch (err) {
        showSpinner(false);
        showMessage("Failed: " + err.message, "error");
        resultsContainer.innerHTML = `<pre style="color:var(--danger);font-size:13px;">${err.message}</pre>`;
    }
}

function clearForm() {
    el("numResources").value = "3";
    el("capacities").value = "";
    el("numTasks").value = "4";
    el("demands").value = "";
    resultsContainer.innerHTML =
        '<p class="muted">No results yet. Click <strong>Run Allocation</strong> to start.</p>';
    capacityContainer.style.display = "none";
    exportBtn.style.display = "none";
    chartCard.style.display = "none";
    message.textContent = "";
}

// theme toggle (store in localStorage)
function applyTheme(theme) {
    if (theme === "light") document.documentElement.classList.add("light-mode");
    else document.documentElement.classList.remove("light-mode");
    localStorage.setItem("theme", theme);
}
themeToggle.addEventListener("click", () => {
    const cur = localStorage.getItem("theme") || "dark";
    applyTheme(cur === "dark" ? "light" : "dark");
});

// Auto-fill example values on page load to demo quickly
document.addEventListener("DOMContentLoaded", () => {
    if (!el("capacities").value) el("capacities").value = "10,8,12";
    if (!el("demands").value) el("demands").value = "4,6,11,8";
    const theme = localStorage.getItem("theme") || "dark";
    applyTheme(theme);
});

runBtn.addEventListener("click", runAllocation);
clearBtn.addEventListener("click", clearForm);
