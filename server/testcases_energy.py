# !pip install pyJoules numpy pytest tqdm statistics

# Run this command for giving access to rapl counter
# sudo chmod -R a+r /sys/class/powercap/intel-rapl

import pytest
import os
import sys
import subprocess
import time
from statistics import median
from pyJoules.energy_meter import EnergyContext
from pyJoules.handler.csv_handler import CSVHandler
from tqdm import tqdm
from pyJoules.handler import EnergyHandler

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO_DIR = os.path.join(BASE_DIR, "repos")

REPOS = {
    "black": {
        "path": os.path.join(REPO_DIR, "black"),
        "ignore": ["tests/test_blackd.py"]
    },
    "requests": {
        "path": os.path.join(REPO_DIR, "requests"),
        "ignore": []
    },
    "flask": {
        "path": os.path.join(REPO_DIR, "flask"),
        "ignore": []
    }
}

class MemoryHandler(EnergyHandler):
    """A simple handler to keep energy traces in memory."""
    def __init__(self):
        super().__init__()
        self.traces = []

    def process(self, trace):
        self.traces.append(trace)

class MultiHandler(EnergyHandler):
    """Wraps multiple handlers so pyJoules can process them at the same time."""
    def __init__(self, handlers):
        super().__init__()
        self.handlers = handlers

    def process(self, trace):
        for handler in self.handlers:
            handler.process(trace)

# Get the absolute path to the data directory
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
csv_handler = CSVHandler(os.path.join(data_dir, "test_energy_meta.csv"))
meta_csv_path = os.path.join(data_dir, "test_energy.csv")

# Create the meta CSV file if it doesn't exist
if not os.path.exists(meta_csv_path):
    with open(meta_csv_path, "w") as f:
        f.write("timestamp;repo;test_name;median_duration;median_package;median_core\n")

os.chdir("../repos/black")

def measure_idle_power(duration=5):
    """
    Measure baseline idle CPU power using pyJoules.
    Returns power in microjoules per second.
    """

    memory_handler = MemoryHandler()

    with EnergyContext(handler=memory_handler, start_tag="idle_measure"):
        time.sleep(duration)

    trace = memory_handler.traces[-1]
    sample = trace[0]

    package = sample.energy.get("package_0", 0)
    core = sample.energy.get("core_0", 0)

    total_energy = package + core

    idle_power = total_energy / duration  # µJ per second

    print(f"Idle power estimated: {idle_power:.2f} µJ/s")

    return idle_power

class TestCollector:
    def __init__(self):
        self.tests = []

    def pytest_collection_modifyitems(self, session, config, items):
        for item in items:
            self.tests.append(item.nodeid)

def get_tests(ignore_files=None):

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--collect-only",
        "-q"
    ]

    if ignore_files:
        for f in ignore_files:
            cmd.append(f"--ignore={f}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    tests = []

    for line in result.stdout.splitlines():
        if "::test" in line:
            tests.append(line.strip())

    return tests

def run_test(test_name, csv_handler):
    tag = f"{test_name}_run"
    
    # Initialize the memory handler for this specific run
    memory_handler = MemoryHandler()
    
    # Wrap both handlers into the single MultiHandler
    multi_handler = MultiHandler([csv_handler, memory_handler])
    
    start = time.perf_counter()

    # Pass the SINGLE multi_handler to EnergyContext
    with EnergyContext(handler=multi_handler, start_tag=tag):
        subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--disable-warnings", test_name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    duration = time.perf_counter() - start

    # 1. Extract the full trace container from our memory handler
    trace = memory_handler.traces[-1]
    
    # 2. Extract the specific sample from inside the trace
    sample = trace[0]
    
    # 3. Now extract the values from the sample's energy dictionary
    package = sample.energy.get("package_0", 0)
    core = sample.energy.get("core_0", 0)

    return duration, package, core

def main():
    idle_power = measure_idle_power()

    for repo_name, cfg in REPOS.items():

        print(f"\n===== Processing {repo_name} =====")

        repo_path = os.path.abspath(cfg["path"])
        os.chdir(repo_path)

        tests = get_tests(cfg["ignore"])

        for test in tqdm(tests[1:21], desc=f"Running {repo_name}"):

            subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "--disable-warnings", test],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            durations = []
            packages = []
            cores = []

            for i in range(5):
                duration, package, core = run_test(test, csv_handler)
                durations.append(duration)
                packages.append(package)
                cores.append(core)

            median_duration = median(durations)
            median_package = median(packages)
            median_core = median(cores)

            idle_energy = idle_power * median_duration

            corrected_package = max(median_package - idle_energy, 0)
            corrected_core = max(median_core - idle_energy, 0)

            timestamp = time.time()

            tag = f"{repo_name}:{test}"

            with open(meta_csv_path, "a") as f:
                f.write(
                    f"{timestamp};{repo_name};{test};{median_duration};{corrected_package};{corrected_core}\n"
                )

    csv_handler.save_data()

    print("Energy data saved to CSV")


if __name__ == "__main__":  
    main()