# Energy Attribution Model

## Overview

EnergyMap performs energy attribution by transforming test-level energy measurements into module-level energy estimates.

Since hardware energy counters provide only aggregate measurements for entire executions, EnergyMap infers module-level energy consumption by combining execution traces with proportional attribution based on execution time.

---

## Problem Formulation

Let T denote the set of executed test cases. For each test case t ∈ T:

* E_t: total energy consumption of test case t
* M_t: set of modules executed during t
* w(m, t): normalized execution-time weight of module m in test t

The objective is to estimate energy E_m for each module m.

---

## Attribution Model

For each test case t, energy is distributed across modules using precomputed execution-time weights:

E(m, t) = w(m, t) × E_t

These weights are derived from execution traces and represent the relative time spent in each module during the test case.

---

## Internal vs Dependency Attribution

EnergyMap distinguishes between:

* **Internal modules** (top-level project modules)
* **Dependencies** (stdlib and external modules)

During attribution:

* Energy contributions are first assigned to modules
* Dependency energy is tracked separately under parent modules

For each module M:

* Total attributed energy: E_module
* Dependency energy: E_deps
* Self energy is computed as:

E_self = max(0, E_module − E_deps)

This ensures that module energy is decomposed into:

* Self execution
* Dependency contributions

---

## Aggregation Across Test Cases

For each module m, let T_m ⊆ T be the set of test cases where m appears.

Energy is aggregated as:

E_m = mean(E_self(m, t) for all t ∈ T_m)

Only test cases where the module is executed are considered.

Similarly, dependency energies are aggregated:

E_dep(M, D) = mean(E_dep(M, D, t) over relevant test cases)

This preserves parent-child relationships during aggregation.

---

## View Construction

EnergyMap constructs two complementary views:

### Hierarchical (Nested) View

* Internal modules form the top level
* Each module includes:

  * Self energy
  * Energy contributions from dependencies

Total module energy:

E_total(M) = E_self(M) + sum(E_dep(M, D))

Dependencies are shown under their parent modules.

---

### Flat View

* Internal modules → self energy only
* Dependencies → aggregated globally across all parent modules

This enables direct comparison across modules and dependencies.

---

## Assumptions

* Execution time is proportional to energy consumption at the module level
* Execution traces accurately capture module behavior
* Test cases provide representative coverage of the system

---

## Limitations

* Attribution is approximate due to reliance on time-based weighting
* Hardware counters provide only coarse-grained measurements
* Attribution accuracy depends on test coverage
* Dependency attribution is context-sensitive and may vary across execution paths
* DRAM and other non-package energy components are not included

---

## Summary

EnergyMap uses a proportional attribution model combined with hierarchical dependency tracking to estimate module-level energy consumption.

By separating self and dependency energy and aggregating across test cases, the system provides both detailed and high-level views of energy distribution within a software system.
