import csv
import statistics
from collections import defaultdict


ENERGY_FILE = "../data/test_energy.csv"
MAP_FILE = "../data/testcase_module_map.csv"
OUTPUT_FILE = "../data/module_energy_stats.csv"

def extract_test_name(nodeid):
    """
    Convert pytest nodeid into plain testcase name.
    Example:
    tests/test_black.py::BlackTestCase::test_example -> test_example
    """
    return nodeid.split("::")[-1]

def load_energy():
    energy_data = {}

    with open(ENERGY_FILE) as f:
        reader = csv.reader(f, delimiter=";")

        for row in reader:
            timestamp, repo, nodeid, duration, package, core = row

            testcase = extract_test_name(nodeid)

            energy_data[(repo, testcase)] = {
                "package": float(package),
                "core": float(core)
            }

    return energy_data


def load_mapping():
    """
    Load testcase → module mapping.
    Returns dict:
        key = (repo, testcase)
        value = list of modules
    """

    mapping = defaultdict(list)

    with open(MAP_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:

            repo = row["repo"]
            testcase = row["testcase"]
            module = row["module"]

            if module == "UNMAPPED":
                continue

            mapping[(repo, testcase)].append(module)

    return mapping

def aggregate_energy(energy_data, mapping):

    module_energy = defaultdict(lambda: {
        "package": [],
        "core": []
    })

    matched = 0

    for key in energy_data:

        if key not in mapping:
            continue

        matched += 1

        energies = energy_data[key]
        modules = mapping[key]

        package_share = energies["package"] / len(modules)
        core_share = energies["core"] / len(modules)

        for module in modules:
            module_energy[module]["package"].append(package_share)
            module_energy[module]["core"].append(core_share)

    print("Matched testcases:", matched)

    return module_energy


def compute_stats(module_energy):

    rows = []

    for module, energies in module_energy.items():

        pkg = energies["package"]
        core = energies["core"]

        pkg_mean = statistics.mean(pkg)
        pkg_median = statistics.median(pkg)
        pkg_var = statistics.stdev(pkg) if len(pkg) > 1 else 0
        pkg_best = min(pkg)
        pkg_worst = max(pkg)

        core_mean = statistics.mean(core)
        core_median = statistics.median(core)
        core_var = statistics.stdev(core) if len(core) > 1 else 0
        core_best = min(core)
        core_worst = max(core)

        rows.append([
            module,
            pkg_mean,
            pkg_median,
            pkg_var,
            pkg_best,
            pkg_worst,
            core_mean,
            core_median,
            core_var,
            core_best,
            core_worst,
            len(pkg)
        ])

    return rows


def write_output(rows):

    with open(OUTPUT_FILE, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "module",

            "package_mean",
            "package_median",
            "package_stdev",
            "package_best",
            "package_worst",

            "core_mean",
            "core_median",
            "core_stdev",
            "core_best",
            "core_worst",

            "num_testcases"
        ])

        writer.writerows(rows)


def main():

    print("Loading energy data...")
    energy_data = load_energy()

    print("Loading testcase-module mapping...")
    mapping = load_mapping()

    print("Aggregating energy per module...")
    print("Energy entries:", len(energy_data))
    print("Mapping entries:", len(mapping))
    module_energy = aggregate_energy(energy_data, mapping)

    print("Computing statistics...")
    rows = compute_stats(module_energy)

    print("Writing output...")
    write_output(rows)

    print(f"Done. Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()