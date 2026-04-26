# EnergyMap

## Overview

EnergyMap is a Python-based framework that measures and attributes energy consumption at the **module level** in Python programs.

Unlike traditional profilers that focus on execution time or memory usage, EnergyMap introduces **energy as a first-class metric** for software analysis. It enables developers to identify *energy hotspots* within their codebase and make targeted, energy-efficient optimizations.

---

## Why EnergyMap?

Modern software systems are increasingly complex and dependency-heavy, yet developers lack visibility into how energy is consumed across different parts of the system.

EnergyMap addresses this gap by:

* Identifying **which parts of the code consume the most energy**
* Going beyond processes to provide **fine-grained module-level insights**
* Accounting for **energy contributions from dependencies**
* Enabling **data-driven optimization for energy efficiency**

---

## Key Features

### 1. Test-Driven Energy Profiling

EnergyMap operates on existing test suites, eliminating the need to manually define execution workflows.

* Works with any Python project that has a reasonably comprehensive test suite
* Scales naturally with project complexity
* Avoids intrusive instrumentation of production code paths

---

### 2. Fine-Grained Energy Attribution

Instead of reporting aggregate energy usage, EnergyMap identifies:

* Energy consumption at the **module level**
* Relative contribution of each component
* Precise **energy hotspots** within the system

---

### 3. Dependency-Aware Analysis

Modern applications rely heavily on external libraries. EnergyMap explicitly accounts for:

* Standard library usage
* External dependencies (e.g., third-party packages)
* Their contribution to total energy consumption

---

### 4. Visual Energy Maps

EnergyMap provides intuitive visualizations to help users:

* Compare modules at a glance
* Explore nested dependency contributions
* Identify optimization opportunities quickly

---

## How It Works (Pipeline Overview)

EnergyMap follows a multi-stage pipeline:

### Step 1: Test Execution & Energy Measurement

* The project's test suite is executed
* Energy consumption is measured for each test case
* Noise mitigation techniques are applied to improve accuracy

---

### Step 2: Execution Tracing

* During test execution, all accessed modules are recorded
* Includes:

  * Internal project modules
  * Standard library modules
  * External dependencies

---

### Step 3: Energy Attribution & Aggregation

Energy data and execution traces are combined to compute:

#### View 1: Hierarchical Module View

* Internal modules at the top level
* Each module includes:

  * Self energy consumption
  * Energy contribution from dependencies
* Interactive breakdown into:

  * Standard library usage
  * External dependencies

#### View 2: Flat Energy Map

* Internal modules → self energy only
* Standard library modules → grouped by name
* External dependencies → grouped by package

---

### Step 4: Data Storage & API Layer

* Processed data is stored in a database
* API endpoints are exposed for querying energy insights

---

### Step 5: Visualization Layer

* A React-based frontend renders interactive energy maps
* Enables intuitive exploration of energy distribution across the system


---

## Quickstart

> ⚠️ **Note:** Running full energy measurement experiments requires specific hardware and system-level access (e.g., Intel RAPL counters on Linux).
> See detailed setup instructions in `docs/running_experiments.md`.

EnergyMap supports two primary workflows:

### 1. Visualizing Precomputed Results (Recommended)

If you want to explore EnergyMap without setting up hardware dependencies:

```bash
python server/init_db.py
python server/populate_db.py
uvicorn server.api:app --port 8080
```

Then start the frontend:

```bash
cd lib
npm install
npm run dev
```

Open the application in your browser to explore energy maps.

---

### 2. Running Energy Profiling on Your Own Project

Running EnergyMap on a new project requires:

* A Python project with a test suite
* Supported hardware (Intel RAPL)
* Proper system permissions

Refer to:
 `docs/running_experiments.md`

---

## Evaluated Projects

EnergyMap has been evaluated on real-world Python projects to demonstrate its applicability:

* Flask — a widely used web framework
* Black — a production-grade code formatter
* Requests — a popular HTTP client library

These projects were selected to cover diverse workloads, including web applications, developer tooling, and network-bound systems.

Precomputed experiment data for these projects is included in the repository and can be explored using the visualization workflow described above.


---

## Limitations

* Requires sufficiently comprehensive test coverage for meaningful results
* Energy attribution is approximate and based on execution traces
* Dependent on hardware energy counters (e.g., Intel RAPL)
* Measurement noise may affect accuracy despite mitigation techniques

---

## 📂 Repository Structure

```text
data/          # CSV files of the pre-conducted experiments
docs/          # Detailed documentation
lib/           # React frontend for visualization
server/        # Backend API and data processing
```

---

## Documentation

For more details:

* Architecture → `docs/architecture.png`
* Energy Pipeline → `docs/energy_pipeline.md`
* Attribution Model → `docs/attribution.md`
* Installation Guide → `docs/running_experiments.md`