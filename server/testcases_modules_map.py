"""
Testcase → Module Energy Attribution using PyInstrument

Profiles each pytest testcase individually using pyinstrument, traverses the
resulting call tree, classifies every frame as internal / stdlib / external,
and produces a two-level hierarchical energy-attribution CSV.

Output columns:
    repo, test_file, testcase, module, weight, category, parent_module
"""

import csv
import os
import re
import site
import subprocess
import sys
import sysconfig
from collections import defaultdict

from pyinstrument.session import Session

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO_DIR = os.path.join(BASE_DIR, "repos")
DATA_DIR = os.path.join(BASE_DIR, "data")

OUTPUT = os.path.join(DATA_DIR, "testcase_module_map.csv")

REPOS = {
    "black": {
        "tests": os.path.join(REPO_DIR, "black", "tests"),
        "src": os.path.join(REPO_DIR, "black", "src", "black"),
        "pkg": "black",
        "path": os.path.join(REPO_DIR, "black"),
        "ignore": ["tests/test_blackd.py"],
    },
    "requests": {
        "tests": os.path.join(REPO_DIR, "requests", "tests"),
        "src": os.path.join(REPO_DIR, "requests", "src", "requests"),
        "pkg": "requests",
        "path": os.path.join(REPO_DIR, "requests"),
        "ignore": [],
    },
    "flask": {
        "tests": os.path.join(REPO_DIR, "flask", "tests"),
        "src": os.path.join(REPO_DIR, "flask", "src", "flask"),
        "pkg": "flask",
        "path": os.path.join(REPO_DIR, "flask"),
        "ignore": [],
    },
}

# ---------------------------------------------------------------------------
# Module classification helpers
# ---------------------------------------------------------------------------

# Pre-compute site-packages paths FIRST (checked before stdlib to avoid
# false positives when venv site-packages dirs live under stdlib-like paths).
_SITE_PACKAGES_PATHS: list[str] = []
for _p in site.getsitepackages() + [site.getusersitepackages()]:
    if isinstance(_p, str) and os.path.isdir(_p):
        _SITE_PACKAGES_PATHS.append(os.path.realpath(_p))

# Standard-library paths — only 'stdlib' and 'platstdlib'.
# Do NOT include 'purelib' / 'platlib' — those are site-packages.
_STDLIB_PATHS: list[str] = []
for _key in ("stdlib", "platstdlib"):
    _p = sysconfig.get_paths().get(_key)
    if _p and os.path.isdir(_p):
        _STDLIB_PATHS.append(os.path.realpath(_p))


def classify_module(
    file_path: str | None,
    src_dir: str,
    repo_name: str,
    pkg_name: str,
) -> tuple[str | None, str | None]:
    """Classify a frame's file_path into (module_name, category).

    Categories:
        "internal"  – belongs to the repository under test
        "stdlib"    – Python standard library
        "external"  – third-party site-packages dependency

    Returns (None, None) for synthetic frames or unclassifiable paths.
    """
    if file_path is None:
        return None, None

    real_path = os.path.realpath(file_path)
    abs_src = os.path.realpath(src_dir)

    # ---- INTERNAL: file is inside the repo's source tree ----
    if real_path.startswith(abs_src + os.sep) or real_path == abs_src:
        rel = os.path.relpath(real_path, os.path.dirname(abs_src))
        # e.g.  black/parsing.py  →  black.parsing
        module = rel.replace(os.sep, ".").removesuffix(".py")
        # strip __init__ suffix
        module = re.sub(r"\.__init__$", "", module)
        return module, "internal"

    def clean_name(name: str) -> str:
        if name.endswith(".so") or name.endswith(".pyd"):
            name = name.split(".")[0]
        name = re.sub(r"\.py$", "", name)
        name = re.sub(r"\.dist-info$", "", name)
        name = re.sub(r"\.egg-info$", "", name)
        name = name.replace("__init__", "")
        return name

    # ---- EXTERNAL: check site-packages BEFORE stdlib ----
    # In virtual environments, site-packages directories often live under
    # paths that also match stdlib prefixes (e.g. .venv/lib64/python3.14/).
    # Checking site-packages first prevents false stdlib classification.
    for sp in _SITE_PACKAGES_PATHS:
        if real_path.startswith(sp + os.sep):
            rel = os.path.relpath(real_path, sp)
            top = rel.split(os.sep)[0]
            return clean_name(top), "external"

    # ---- STDLIB: file lives under a stdlib directory ----
    for sp in _STDLIB_PATHS:
        if real_path.startswith(sp + os.sep):
            rel = os.path.relpath(real_path, sp)
            top = rel.split(os.sep)[0]
            return clean_name(top), "stdlib"

    # ---- Could be a built-in C module (e.g. <built-in>) ----
    if "<built-in>" in file_path:
        return None, None

    return None, None


# ---------------------------------------------------------------------------
# Call-tree traversal
# ---------------------------------------------------------------------------


def traverse(
    frame,
    src_dir: str,
    repo_name: str,
    pkg_name: str,
    parent_internal_module: str | None,
    internal_time: dict[str, float],
    stdlib_time: dict[str, dict[str, float]],
    external_time: dict[str, dict[str, float]],
) -> None:
    """Recursively walk a pyinstrument Frame tree and accumulate time.

    Level 1 – internal modules get their inclusive time recorded.
    Level 2 – stdlib / external time is attributed to the nearest internal
              ancestor module.
    """
    if frame is None:
        return

    module_name, category = classify_module(
        frame.file_path, src_dir, repo_name, pkg_name
    )

    # Determine the current internal ancestor for stdlib/external attribution
    current_internal = parent_internal_module

    if category == "internal" and module_name:
        current_internal = module_name
        # Add *self* time to this internal module (not inclusive time,
        # because we recurse into children separately).
        self_time = getattr(frame, "total_self_time", 0.0) or 0.0
        # total_self_time may be 0 for non-leaf frames; that's fine —
        # children will contribute their own self-time.
        internal_time[module_name] += self_time

    elif category == "stdlib" and module_name and current_internal:
        # Attribute this frame's self time to the nearest internal ancestor
        self_time = getattr(frame, "total_self_time", 0.0) or 0.0
        stdlib_time[current_internal][module_name] += self_time

    elif category == "external" and module_name and current_internal:
        self_time = getattr(frame, "total_self_time", 0.0) or 0.0
        external_time[current_internal][module_name] += self_time

    # Recurse into children
    for child in frame.children:
        traverse(
            child,
            src_dir,
            repo_name,
            pkg_name,
            current_internal,
            internal_time,
            stdlib_time,
            external_time,
        )


# ---------------------------------------------------------------------------
# Test discovery
# ---------------------------------------------------------------------------


def discover_tests(
    repo_path: str,
    test_dir: str,
    ignore_files: list[str] | None = None,
) -> list[tuple[str, str, str]]:
    """Use ``pytest --collect-only`` to discover all tests.

    This handles both free-function tests and class-based test methods
    (e.g. ``BlackTestCase::test_one_empty_line``).

    Returns a list of (test_file_relpath, test_name, node_id) tuples.
    """
    ignore_files = ignore_files or []

    cmd = [
        sys.executable, "-m", "pytest",
        "--collect-only", "-q",
    ]
    for ig in ignore_files:
        cmd.append(f"--ignore={ig}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_path,
    )

    tests: list[tuple[str, str, str]] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if "::" not in line or not line.endswith("]") and "test" not in line.lower():
            continue
        # Lines look like:  tests/test_black.py::BlackTestCase::test_bpo_2142_workaround
        #               or: tests/test_format.py::test_simple_format_functions
        if "::" not in line:
            continue

        node_id = line.strip()
        parts = node_id.split("::")
        file_part = parts[0]  # e.g. tests/test_black.py
        test_name = parts[-1]  # last part is always the function name

        # Relative to the test directory
        rel_test = os.path.relpath(
            os.path.join(repo_path, file_part),
            test_dir,
        )

        tests.append((rel_test, test_name, node_id))

    return tests


# ---------------------------------------------------------------------------
# Profiled test execution
# ---------------------------------------------------------------------------


def run_test_with_profiler(
    repo_path: str, node_id: str
) -> "Session | None":
    """Run a single pytest test under pyinstrument profiling in a subprocess.

    This avoids in-process pytest state contamination (ImportPathMismatchError).
    Returns the loaded pyinstrument Session object, or None if profiling failed.
    """
    import tempfile
    
    # Save and restore cwd
    original_cwd = os.getcwd()
    try:
        os.chdir(repo_path)

        # Use a temporary file for the session
        fd, temp_path = tempfile.mkstemp(suffix=".pyisession")
        os.close(fd)
        
        cmd = [
            sys.executable, "-m", "pyinstrument",
            "-r", "pyisession",
            "-o", temp_path,
            "-m", "pytest",
            "-x", "-q", "--tb=no", "--no-header", "--disable-warnings", node_id
        ]
        
        # We need to include repo_path in PYTHONPATH to ensure the src is importable
        env = os.environ.copy()
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{repo_path}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = repo_path
            
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            session = Session.load(temp_path)
            os.remove(temp_path)
            return session
        else:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None
            
    except Exception as exc:
        print(f"  [ERROR] Profiling failed for {node_id}: {exc}")
        return None
    finally:
        os.chdir(original_cwd)


# ---------------------------------------------------------------------------
# Per-test processing
# ---------------------------------------------------------------------------


def process_test(
    session: "Session",
    src_dir: str,
    repo_name: str,
    pkg_name: str,
) -> list[dict]:
    """Process a single profiler session into attribution rows.

    Returns a list of dicts with keys:
        module, weight, category, parent_module
    """
    if session is None:
        return []

    root = session.root_frame()
    if root is None:
        return []

    # Accumulators
    internal_time: dict[str, float] = defaultdict(float)
    stdlib_time: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    external_time: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    traverse(
        root,
        src_dir,
        repo_name,
        pkg_name,
        parent_internal_module=None,
        internal_time=internal_time,
        stdlib_time=stdlib_time,
        external_time=external_time,
    )

    if not internal_time:
        return []

    # ---- Level 1: top-level internal attribution ----
    # Each internal module's total = its own self-time + all stdlib/external
    # time attributed to it.
    total_per_internal: dict[str, float] = {}
    for mod in set(internal_time) | set(stdlib_time) | set(external_time):
        total = internal_time.get(mod, 0.0)
        total += sum(stdlib_time.get(mod, {}).values())
        total += sum(external_time.get(mod, {}).values())
        if total > 0:
            total_per_internal[mod] = total

    grand_total = sum(total_per_internal.values())
    if grand_total <= 0:
        return []

    rows: list[dict] = []

    # Level 1 rows (internal modules)
    for mod, t in sorted(total_per_internal.items(), key=lambda x: -x[1]):
        rows.append(
            {
                "module": mod,
                "weight": round(t / grand_total, 6),
                "category": "internal",
                "parent_module": "",
            }
        )

    # ---- Level 2: drill-down into each internal module ----
    for parent_mod in sorted(total_per_internal):
        parent_total = total_per_internal[parent_mod]
        if parent_total <= 0:
            continue

        # stdlib children
        for child_mod, ct in sorted(
            stdlib_time.get(parent_mod, {}).items(), key=lambda x: -x[1]
        ):
            if ct > 0:
                rows.append(
                    {
                        "module": child_mod,
                        "weight": round(ct / grand_total, 6),
                        "category": "stdlib",
                        "parent_module": parent_mod,
                    }
                )

        # external children
        for child_mod, ct in sorted(
            external_time.get(parent_mod, {}).items(), key=lambda x: -x[1]
        ):
            if ct > 0:
                rows.append(
                    {
                        "module": child_mod,
                        "weight": round(ct / grand_total, 6),
                        "category": "external",
                        "parent_module": parent_mod,
                    }
                )

    return rows


# ---------------------------------------------------------------------------
# Repo-level processing
# ---------------------------------------------------------------------------


def process_repo(
    repo_name: str,
    cfg: dict,
    writer: csv.writer,
) -> None:
    """Discover and profile all tests in a repository."""
    print(f"\n{'='*60}")
    print(f"  Processing repo: {repo_name}")
    print(f"{'='*60}")

    src_dir = cfg["src"]
    repo_path = cfg["path"]
    pkg_name = cfg["pkg"]

    tests = discover_tests(
        repo_path,
        cfg["tests"],
        ignore_files=cfg.get("ignore", []),
    )
    print(f"  Discovered {len(tests)} test functions")

    for i, (test_file, test_name, node_id) in enumerate(tests, 1):
        print(f"  [{i}/{len(tests)}] {node_id} ... ", end="", flush=True)

        session = run_test_with_profiler(repo_path, node_id)

        if session is None:
            writer.writerow([repo_name, test_file, test_name, "UNMAPPED", 0.0, "", ""])
            print("SKIP (profiler error)")
            continue

        rows = process_test(session, src_dir, repo_name, pkg_name)

        if not rows:
            writer.writerow([repo_name, test_file, test_name, "UNMAPPED", 0.0, "", ""])
            print("SKIP (no internal modules)")
            continue

        for row in rows:
            writer.writerow(
                [
                    repo_name,
                    test_file,
                    test_name,
                    row["module"],
                    row["weight"],
                    row["category"],
                    row["parent_module"],
                ]
            )

        n_internal = sum(1 for r in rows if r["category"] == "internal")
        n_drill = len(rows) - n_internal
        print(f"OK ({n_internal} internal, {n_drill} drill-down)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"Output: {OUTPUT}")
    print(f"Repos:  {', '.join(REPOS.keys())}")

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["repo", "test_file", "testcase", "module", "weight", "category", "parent_module"]
        )

        for repo_name, cfg in REPOS.items():
            process_repo(repo_name, cfg, writer)

    print(f"\nDONE → {OUTPUT}")


if __name__ == "__main__":
    main()