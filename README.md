# EnergyMap: Module-Level Energy Profiling for Python

EnergyMap is an end-to-end pipeline designed to measure, attribute, and visualize the energy consumption of Python software at the module level. By combining hardware-level energy measurements (Intel RAPL) with static analysis (AST), EnergyMap provides insights into which parts of a codebase are most energy-intensive.

## 🏗️ Architecture and Pipeline

The pipeline is designed to move from raw test execution to high-level energy visualizations through several distinct stages:

### 1. Repository Setup & Test Collection
The system targets existing Python projects (currently `black`, `requests`, and `flask`). It automatically collects test cases using `pytest` to identify the functional entry points of the application.

### 2. Static Analysis & Mapping (AST)
Using Python's `ast` (Abstract Syntax Tree) module, EnergyMap performs static analysis on the test suite:
- It identifies which source modules are imported and called within each test case.
- It generates a mapping between individual test cases and the specific source code modules they exercise.

### 3. Energy Measurement (RAPL)
Energy is measured using Intel's **Running Average Power Limit (RAPL)** interface via the `pyJoules` library:
- **Idle Baseline:** Before running tests, the system measures the baseline idle power of the CPU (package and core).
- **Test Execution:** Each test is executed multiple times (default: 5) to account for variability.
- **Energy Correction:** The idle power consumption is subtracted from the measured energy during test execution to isolate the energy cost of the software itself.
- **Wake Management:** Uses `wakepy` to ensure the system remains in a high-performance state and does not sleep during long-running measurement sessions.

### 4. Data Sanitization & Aggregation
Raw energy data is processed through a validation pipeline:
- **Sanitization:** Removes malformed or suspicious data points.
- **Aggregation:** Distributes the energy cost of a test case across all the modules it exercised. If a test case exercises $N$ modules, the measured energy is shared among them to estimate per-module consumption.
- **Statistics:** Computes Mean, Median, Variance, Best-case, and Worst-case energy consumption for every module.

### 5. Data Storage & API
The processed statistics are stored in a **SQLite** database (`energy_stats.db`). A **FastAPI** backend serves this data through a RESTful API, allowing the frontend to query energy profiles by project.

### 6. Visualization Dashboard
A **React**-based dashboard provides an interactive interface to explore the energy data:
- **Treemaps:** For hierarchical visualization of energy distribution across modules.
- **Bar/Pie Charts:** For comparing energy consumption between different modules or projects.
- **Statistical Cards:** To view detailed metrics like variance and worst-case scenarios.

---

## 🔬 Performed Experiments

The tool has been validated through several experimental runs on popular open-source repositories:
1.  **Black (Code Formatter):** Analyzed the energy cost of various formatting operations and their corresponding modules.
2.  **Requests (HTTP Library):** Measured energy consumption during different network simulation tests.
3.  **Flask (Web Framework):** Profiled the overhead of routing, request handling, and template rendering.

---

## 📁 Repository Structure

```text
EnergyMap/
├── data/               # CSV data (raw measurements, mappings, and final stats)
├── docs/               # Architectural diagrams and documentation
├── lib/                # Frontend application (React + Vite)
│   ├── src/            # Dashboard components and services
│   └── package.json    # Frontend dependencies
├── repos/              # Target repositories for analysis (black, flask, requests)
├── server/             # Backend and Data Pipeline scripts
│   ├── api.py          # FastAPI Server
│   ├── wake.py         # System wake management
│   ├── aggregation.py  # Energy attribution logic
│   ├── testcases_energy.py  # RAPL measurement script
│   ├── testcases_modules_map.py # AST mapping script
│   └── init_db.py      # Database setup and population
├── energy_stats.db     # SQLite Database (generated)
└── README.md           # Project overview (this file)
```

---

## 🚀 Execution Instructions

### Prerequisites
- **Intel CPU** with RAPL support.
- **Linux OS** (Tested on Fedora/Ubuntu).
- **Permissions:** RAPL counters require read access. Run:
  ```bash
  sudo chmod -R a+r /sys/class/powercap/intel-rapl
  ```

### Backend & Data Pipeline
1.  **Install Dependencies:**
    ```bash
    pip install fastapi pyJoules wakepy pytest tqdm statistics sqlite3
    ```
2.  **Generate Data (In order):**
    ```bash
    cd server
    python testcases_modules_map.py  # Create mapping
    python testcases_energy.py       # Measure energy (Requires RAPL)
    python energy_csv_sanitization.py # Clean data
    python aggregation.py            # Aggregate energy

### Frontend dashboard + FastAPI setup:
1. Run "python server/init_db.py && python server/populate_db.py".
2. Start the server using command "uvicorn server.api:app --port 8080".
3. Start frontend by change directory to lib ("cd lib" from root) then using command "npm install" 
followed by "npm run dev".
