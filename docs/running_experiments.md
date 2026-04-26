# Running Energy Experiments

## Overview

This document describes how to run the full EnergyMap backend pipeline to generate energy measurements and module-level attribution from scratch.

> ⚠️ These steps require specific hardware support and system-level permissions.
> For most users, we recommend using the precomputed datasets included in this repository.

---

## System Requirements

Energy measurement relies on hardware performance counters and is therefore platform-dependent.

### Hardware

* Intel CPU with **RAPL (Running Average Power Limit)** support
* x86_64 architecture recommended

### Operating System

* Linux (tested on Fedora-based systems)

### Permissions

* Access to RAPL counters:

```bash
sudo chmod -R a+r /sys/class/powercap/intel-rapl
```

> ⚠️ Root privileges are required for energy measurement.

---

## Software Dependencies

### Python Environment

* Python 3.10+

Install required packages inside `server/`:

```bash
pip install -r requirement.txt
```

---

## Repository Setup

Clone the repository and ensure the following structure:

```id="c1nhl9"
EnergyMap/
├── repos/        # Target repositories (flask, black, requests)
├── data/         # Generated CSV files
├── server/       # Backend pipeline scripts
```

---

## Target Repositories

EnergyMap expects Python projects with test suites inside the `repos/` directory.

Example:

```id="80m1hv"
repos/
├── flask/
├── black/
├── requests/
```

Ensure each repository:

* installs correctly
* has a working pytest suite

---

## Execution Pipeline

Run the following steps **in order**.

### Step 0

```bash
python server/wake.py
```

---

### Step 1

```bash
sudo python server/testcases_energy.py
```

---

### Step 2

```bash
python server/energy_csv_sanitization.py
```

---

### Step 3

```bash
python server/energy_csv_validation.py
```

---

### Step 4

```bash
python server/testcases_modules_map.py
```

---

### Step 5

```bash
python server/aggregation.py
```

---

### Step 6

```bash
python server/init_db.py
python server/populate_db.py
```

---

### Step 7

```bash
uvicorn server.api:app --port 8080
```
---

## Notes on Measurement Quality

* Energy readings are **noisy** due to OS scheduling and background processes
* Multiple iterations per test are used to reduce variance
* Idle power is subtracted to improve signal quality
* Results are **approximate**, not exact hardware attribution

---

## Common Issues

### Permission Errors

Ensure RAPL access:

```bash
sudo chmod -R a+r /sys/class/powercap/intel-rapl
```

---

### Missing Energy Readings

* Verify CPU supports RAPL
* Ensure pyJoules is correctly installed

---

### Inconsistent Results

* Close background applications
* Run experiments on an idle system
* Increase number of iterations if needed

---

## Recommended Usage

Due to setup complexity, most users should:

* Use precomputed datasets in `data/`
* Run only:

  * database setup
  * API server
  * frontend visualization

---

## Summary

Running EnergyMap experiments requires:

* Supported hardware (Intel RAPL)
* Controlled execution environment
* Multi-stage pipeline execution

While the process is complex, it enables detailed module-level energy analysis of real-world Python systems.