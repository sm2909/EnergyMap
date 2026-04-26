# EnergyMap Energy Pipeline

## Overview

EnergyMap processes raw execution data through a multi-stage pipeline to transform test-level energy measurements into module-level energy insights.

The pipeline is designed as a sequence of data transformations, where each stage refines, enriches, or aggregates information to enable accurate energy attribution.

EnergyMap follows a **multi-pass pipeline**, where energy measurement and execution tracing are performed separately to reduce interference and improve attribution accuracy.

---

## Pipeline Stages

### Stage 0: Environment Stabilization (Optional)

**Purpose**
Ensure consistent execution conditions during long-running experiments.

**Process**
System sleep and power-saving mechanisms are disabled to prevent interruptions during measurement.

**Notes**

* Improves reliability of long-running measurements
* Optional but recommended for large experiments

---

### Stage 1: Test-Driven Energy Measurement

**Purpose**
Collect raw energy consumption data for individual test cases.

**Input**

* Python repositories with test suites

**Process**

* Test cases are executed in isolation
* Energy consumption is measured using hardware counters (e.g., RAPL via pyJoules)
* Multiple iterations (currently 5) are performed per test case, and the average energy consumption is used to reduce measurement noise.
* Idle power is subtracted from all measurements to remove background noises during calculation

**Output**

* Raw energy traces per test case

**Notes**

* Requires system-level permissions
* Measurement noise is mitigated but not eliminated due to OS scheduling or other background processes.
* Package energy is used for calculations, which includes core, caches, memory controllers; but not DRAM energy.

---

### Stage 2: Data Sanitization

**Purpose**
Ensure structural and numerical integrity of collected energy data.

**Input**

* Raw energy trace data

**Process**

* Remove malformed or incomplete rows
* Validate numeric fields
* Filter out corrupted or anomalous entries

**Output**

* Cleaned energy dataset suitable for downstream processing

---

### Stage 3: Data Validation (Optional)

**Purpose**
Verify correctness and consistency of the sanitized dataset.

**Process**

* Perform structural checks on cleaned data
* Report anomalies or inconsistencies

**Output**

* Validation logs (no data transformation)

---

### Stage 4: Test-to-Module Mapping

**Purpose**
Establish relationships between test cases and the modules they exercise.

**Input**

* Repository source code with test suite.

**Process**

* Execution tracing is performed dynamically using profiling tools (e.g., pyInstrument), rather than static analysis.
* For each test case, all invoked modules are recorded and categorized as:
  * Internal modules (within the project)
  * Standard library modules
  * External dependencies
* Parent-child relationships between modules are also tracked

**Output**

* Test-to-module mapping dataset

**Key Assumption**

Energy attribution is based on the assumption that execution time is proportional to energy consumption at the module level.  
This assumption is widely used in practice due to the lack of fine-grained hardware-level attribution mechanisms and has been found to produce reasonable approximations in this context.

---

### Stage 5: Energy Attribution & Aggregation

**Purpose**
Translate test-level energy measurements into module-level energy estimates.

**Input**

* Cleaned energy dataset
* Test-to-module mapping

**Process**

* Energy measured at the test level is distributed across modules using normalized execution-time weights
* The weights computed in previous step are used to attribute testcase energy to their respective modules.
* Module energies are averaged over all testcases where the module was found to be executed.

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

**Output**

* Module-level energy statistics

**Notes**

* For external and standard library modules, aggregation is performed within the context of their parent modules to avoid misattribution across unrelated execution paths
* Attribution is approximate because it uses the assumption of time based weighting as discussed before.

---

### Stage 6: Data Persistence

**Purpose**
Store processed energy data for efficient querying and visualization.

**Process**

* Insert aggregated module-level statistics into a structured database (SQLite)
* Enforce schema constraints and data consistency

**Output**

* Queryable energy dataset

---

### Stage 7: API Layer

**Purpose**
Expose energy insights to external consumers.

**Process**

* Provide RESTful endpoints for querying module-level energy data
* Support filtering by project and module

**Output**

* JSON responses for downstream applications

---

### Stage 8: Visualization Interface

**Purpose**
Enable interactive exploration of energy data.

**Process**

* Frontend consumes API responses
* Renders hierarchical and flat energy maps

**Output**

* Interactive visual representation of energy distribution

---

## Execution Flow (Script-Level Mapping)

The following scripts implement the pipeline stages:

* Stage 0 → `wake.py`
* Stage 1 → `testcases_energy.py`
* Stage 2 → `energy_csv_sanitization.py`
* Stage 3 → `energy_csv_validation.py`
* Stage 4 → `testcases_modules_map.py`
* Stage 5 → `aggregation.py`
* Stage 6 → `init_db.py`, `populate_db.py`
* Stage 7 → `api.py`

## Key Characteristics

- **Multi-pass design** separating measurement and tracing  
- **Combination of dynamic measurement and static/dynamic tracing**  
- **Statistical aggregation** to reduce noise  
- **Approximate attribution model** based on execution-time weighting 

**For further details, look into `attribution.md`**