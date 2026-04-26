import csv
import statistics
from collections import defaultdict
import os

ENERGY_FILE = "../data/test_energy_clean.csv"
MAP_FILE = "../data/testcase_module_map.csv"
OUTPUT_FILE = "../data/module_energy_stats.csv"

def extract_test_name(nodeid):
    """
    Convert pytest nodeid into plain testcase name.
    """
    return nodeid.split("::")[-1]

def load_energy():
    energy_data = []

    with open(ENERGY_FILE) as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            timestamp, repo, nodeid, duration, package, core = row[:6]
            testcase = extract_test_name(nodeid)
            energy_data.append((repo, testcase, float(package)))

    return energy_data

def process_data(energy_data):
    mapping_by_test = defaultdict(list)
    with open(MAP_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["module"] == "UNMAPPED":
                continue
            mapping_by_test[(row["repo"], row["testcase"])].append(row)

    self_accum = defaultdict(list)  # (repo, M) -> list of E_self
    dep_accum = defaultdict(lambda: defaultdict(list)) # (repo, M) -> D -> list of E_dep
    module_category = {}

    for repo, testcase, e_test in energy_data:
        mappings = mapping_by_test.get((repo, testcase))
        if not mappings:
            continue
            
        test_internal = defaultdict(float)
        test_dep = defaultdict(lambda: defaultdict(float))
        
        for row in mappings:
            module = row["module"]
            weight = float(row["weight"])
            category = row["category"]
            parent = row["parent_module"]
            
            energy = e_test * weight
            
            if parent == "":
                test_internal[module] += energy
                module_category[module] = category
            else:
                test_dep[parent][module] += energy
                module_category[module] = category

        all_M = set(test_internal.keys()) | set(test_dep.keys())
        
        for M in all_M:
            e_module = test_internal.get(M, 0.0)
            e_deps_total = sum(test_dep[M].values())
            e_self = e_module - e_deps_total
            e_self = max(0.0, e_self)
            
            self_accum[(repo, M)].append(e_self)
            if M not in module_category:
                module_category[M] = "internal"
            
        for M, deps in test_dep.items():
            for D, e_dep in deps.items():
                dep_accum[(repo, M)][D].append(e_dep)

    # Averaging
    self_avg = {}
    for (repo, M), energies in self_accum.items():
        self_avg[(repo, M)] = statistics.mean(energies)

    dep_avg = defaultdict(dict)
    for (repo, M), deps in dep_accum.items():
        for D, energies in deps.items():
            dep_avg[(repo, M)][D] = statistics.mean(energies)

    # Build views
    rows = []

    for repo, M in self_avg.keys():
        m_self_avg = self_avg[(repo, M)]
        m_dep_avgs = dep_avg.get((repo, M), {})
        
        # View 1: Nested (hierarchical)
        # Level 1 (internal modules)
        nested_internal_energy = m_self_avg + sum(m_dep_avgs.values())
        rows.append([
            repo,
            M,
            module_category.get(M, "internal"),
            "",
            nested_internal_energy,
            "nested"
        ])
        
        # Level 2 (dependencies)
        for D, d_avg in m_dep_avgs.items():
            rows.append([
                repo,
                D,
                module_category.get(D, "stdlib"),
                M,
                d_avg,
                "nested"
            ])
            
        # View 2: Flat (no hierarchy)
        # Internal
        rows.append([
            repo,
            M,
            module_category.get(M, "internal"),
            "",
            m_self_avg,
            "flat"
        ])

    # View 2: Flat (Dependencies)
    flat_deps = defaultdict(float) # (repo, D) -> sum
    for (repo, M), deps in dep_avg.items():
        for D, d_avg in deps.items():
            flat_deps[(repo, D)] += d_avg

    for (repo, D), total_energy in flat_deps.items():
        rows.append([
            repo,
            D,
            module_category.get(D, "stdlib"),
            "",
            total_energy,
            "flat"
        ])

    return rows

def write_output(rows):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "repo",
            "module",
            "category",
            "parent_module",
            "energy",
            "view"
        ])
        writer.writerows(rows)

def main():
    print("Loading energy data...")
    energy_data = load_energy()

    print("Processing data and building views...")
    rows = process_data(energy_data)

    print("Writing output...")
    write_output(rows)

    print(f"Done. Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()