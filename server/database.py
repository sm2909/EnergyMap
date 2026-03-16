"""
Database caching for experiment results using SQLite.

Stores testcase energy measurements, testcase-to-module mappings,
and module energy statistics so experiments do not need to be rerun.
"""

import csv
import sqlite3

DB_PATH = "data/energy_cache.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS testcase_energy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    test_name TEXT NOT NULL,
    timestamp TEXT,
    duration REAL,
    package_energy REAL,
    dram_energy REAL,
    UNIQUE(project, test_name, timestamp)
);

CREATE TABLE IF NOT EXISTS testcase_module_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    test_name TEXT NOT NULL,
    module TEXT NOT NULL,
    UNIQUE(project, test_name, module)
);

CREATE TABLE IF NOT EXISTS module_energy_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    module TEXT NOT NULL,
    mean REAL,
    median REAL,
    variance REAL,
    best_case REAL,
    worst_case REAL,
    UNIQUE(project, module)
);
"""


def get_connection(db_path=None):
    """Return a new SQLite connection to the given database path."""
    if db_path is None:
        db_path = DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """Create the database and all tables if they do not exist."""
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def load_testcase_energy_csv(project, csv_path, db_path=None):
    """
    Load testcase energy measurements from a pyJoules CSV file.

    Expected CSV columns: timestamp;tag;duration;package_0;dram_0
    Uses semicolon as delimiter (pyJoules default).
    """
    conn = get_connection(db_path)
    try:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = []
            for row in reader:
                rows.append((
                    project,
                    row.get("tag", "").strip(),
                    row.get("timestamp", "").strip(),
                    float(row.get("duration", 0)),
                    float(row.get("package_0", 0)),
                    float(row.get("dram_0", 0)),
                ))
        conn.executemany(
            """INSERT OR REPLACE INTO testcase_energy
               (project, test_name, timestamp, duration, package_energy, dram_energy)
               VALUES (?, ?, ?, ?, ?, ?)""",
            rows,
        )
        conn.commit()
        return len(rows)
    finally:
        conn.close()


def save_testcase_module_map(project, mappings, db_path=None):
    """
    Save testcase-to-module mappings.

    Parameters
    ----------
    project : str
        Project identifier.
    mappings : list[dict]
        Each dict must have keys ``test_name`` and ``module``.
    """
    conn = get_connection(db_path)
    try:
        rows = [
            (project, m["test_name"], m["module"])
            for m in mappings
        ]
        conn.executemany(
            """INSERT OR REPLACE INTO testcase_module_map
               (project, test_name, module)
               VALUES (?, ?, ?)""",
            rows,
        )
        conn.commit()
        return len(rows)
    finally:
        conn.close()


def save_module_energy_stats(project, stats, db_path=None):
    """
    Save aggregated module energy statistics.

    Parameters
    ----------
    project : str
        Project identifier.
    stats : list[dict]
        Each dict must have keys: ``module``, ``mean``, ``median``,
        ``variance``, ``best_case``, ``worst_case``.
    """
    conn = get_connection(db_path)
    try:
        rows = [
            (
                project,
                s["module"],
                s["mean"],
                s["median"],
                s["variance"],
                s["best_case"],
                s["worst_case"],
            )
            for s in stats
        ]
        conn.executemany(
            """INSERT OR REPLACE INTO module_energy_stats
               (project, module, mean, median, variance, best_case, worst_case)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        conn.commit()
        return len(rows)
    finally:
        conn.close()


def get_testcase_energies(project, db_path=None):
    """Return all testcase energy rows for *project* as a list of dicts."""
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """SELECT test_name, timestamp, duration, package_energy, dram_energy
               FROM testcase_energy WHERE project = ?""",
            (project,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_testcase_module_map(project, db_path=None):
    """Return all testcase→module mappings for *project* as a list of dicts."""
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """SELECT test_name, module
               FROM testcase_module_map WHERE project = ?""",
            (project,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_module_energy_stats(project, db_path=None):
    """
    Return cached module energy statistics for *project*.

    Returns a list of dicts with keys: ``module``, ``mean``, ``median``,
    ``variance``, ``best_case``, ``worst_case``.
    """
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """SELECT module, mean, median, variance, best_case, worst_case
               FROM module_energy_stats WHERE project = ?""",
            (project,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
