# EnergyMap Server Scripts

This directory contains the pipeline scripts required to measure execution constraints, sanitize the data, build module-level aggregations, populate the database, and serve it via an API.

## Workflow & Execution Order
To perform a complete data gathering and aggregation cycle, execute the scripts in the following order:

1. **Keep System Awake (Optional):** `python wake.py`
2. **Collect Energy Traces:** `sudo python testcases_energy.py`
3. **Clean the Data:** `python energy_csv_sanitization.py`
4. **Validate Cleanliness (Optional):** `python energy_csv_validation.py`
5. **Map Tests to Modules:** `python testcases_modules_map.py`
6. **Aggregate Energy Statistics:** `python aggregation.py`
7. **Populate Database:** `python init_db.py`
8. **Start API Server:** `uvicorn api:app --reload`

---

## Script Documentation

### 1. `wake.py`
Keeps the system awake while performing long-running processes (e.g., energy logging). 
- **Functionality:** Prevents sleep mechanisms using wakepy natively so execution traces are not interrupted by OS sleep cycles.
- **Requirements:** `wakepy`
- **Inputs:** None.
- **Outputs:** Modifies system state. Does not output files.

### 2. `testcases_energy.py`
Runs unit tests for specified repositories (`black`, `requests`, `flask`) and leverages RAPL (via `pyJoules`) to record package and core energy consumption.
- **Functionality:** Discovers available `pytest` resources in target repos, initiates isolated executions, and computes median energy usage across multiple iterations per test. Corrects power profiles utilizing baseline idle limits.
- **Requirements:** `pyJoules`, `numpy`, `pytest`, `tqdm`, `statistics`. Requires RAPL counter permissions (`sudo chmod -R a+r /sys/class/powercap/intel-rapl`).
- **Inputs:** Test suites present inside the `../repos/` directory.
- **Outputs:** Writes/Appends raw energy trace iterations to `../data/test_energy.csv` alongside a `test_energy_meta.csv` headers generation.

### 3. `energy_csv_sanitization.py`
Cleans up errors, drops invalid metrics, and fixes corrupted rows out of the raw energy traces to prevent future pipeline crashes. 
- **Functionality:** Scans for exact 6-column rows avoiding empty strings, restricts non-floats, and removes known suspicious injection patterns (like HTML strings).
- **Requirements:** Standard python library (`csv`).
- **Inputs:** Raw data in `../data/test_energy.csv`.
- **Outputs:** Safely sanitized tests generated exactly mirroring standard structures inside `../data/test_energy_clean.csv`.

### 4. `energy_csv_validation.py`
Sanity-checks the cleaned CSV to verify formatting patterns, structural rigidity, and absence of outstanding anomalies.
- **Functionality:** A purely read-only diagnostic process providing a terminal validation report detailing total vs valid row ratios and showing examples of errors if there are any lingering mismatches.
- **Requirements:** Standard python library (`csv`).
- **Inputs:** Clean data contained in `../data/test_energy_clean.csv`.
- **Outputs:** Terminal readous and standard output logs. Does not parse out generated files.

### 5. `testcases_modules_map.py`
Performs an Abstract Syntax Tree (AST) analysis on the test code to decipher which function calls correspond to which origin repository source modules.
- **Functionality:** Flattens namespaces and maps localized tests explicitly tracing calls to original repo source Python modules. Connects a test case directly with internal module structures.
- **Requirements:** Standard python libraries (`ast`, `os`, `csv`).
- **Inputs:** Reads Python source code and corresponding test files stationed in `../repos/{project_name}` directories.
- **Outputs:** Translates connections into a CSV mapping table at `../data/testcase_module_map.csv`.

### 6. `aggregation.py`
Merges the sanitized energy consumption files with the localized test-module maps to formulate estimated energy costs per individual independent code module base.
- **Functionality:** Disperses total measured energy across correlated modules invoked. Computes overall average distribution and resolves complex statistical metrics arrayed from module dependencies individually.
- **Requirements:** Standard python libraries (`csv`, `collections`, `statistics`).
- **Inputs:** `../data/test_energy_clean.csv` and `../data/testcase_module_map.csv`.
- **Outputs:** Compiled quantitative metrics output (metrics including pkg_best/pkg_worst and standard deviations) pushed to `../data/module_energy_stats.csv`.

### 7. `init_db.py` & `populate_db.py`
Ingests finalized metrics datasets straight into SQLite database tables making arrays readily query-ready for API access protocols. `init_db.py` natively populates the active API's schema target `energy_stats.db`.
- **Functionality:** Parses the module energy payload row-by-row translating paths locally extracting internal application contexts pushing rows logically replacing redundant conflicts enforcing Unique DB validations.
- **Requirements:** Standard python packages (`sqlite3`, `csv`, `os`).
- **Inputs:** Reads the calculated data set located normally inside `data/module_energy_stats.csv`. (Usually necessitates calling relative roots).
- **Outputs:** Instantiates tables internally modifying `energy_stats.db` SQLite (or `energy_map.db` via `populate_db.py`).

### 8. `api.py`
FastAPI backend service serving analytical measurements directly onto endpoints utilized by external application contexts (e.g. Frontend Web UI).
- **Functionality:** Maintains open CORS middleware policies connecting seamlessly bridging the gap between SQLite datasets fetching `module_energy_stats` relative to explicit query projects.
- **Requirements:** `fastapi`, `sqlite3`, `os` (Served generally under `uvicorn`).
- **Inputs:** HTTP GET requests sent hitting trailing routes like `/api/energy?project=black`. Database points internally dynamically routing `../energy_stats.db`.
- **Outputs:** Transmits clean JSON array payloads organizing variables sequentially responding per query project matched rendering mean/median constraints directly.
