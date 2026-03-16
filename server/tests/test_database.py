"""Tests for server.database – SQLite caching of experiment results."""

import os
import tempfile

import pytest

from server.database import (
    get_module_energy_stats,
    get_testcase_energies,
    get_testcase_module_map,
    init_db,
    load_testcase_energy_csv,
    save_module_energy_stats,
    save_testcase_module_map,
)


@pytest.fixture()
def db_path(tmp_path):
    """Provide a temporary database path and initialise the schema."""
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


@pytest.fixture()
def sample_csv(tmp_path):
    """Create a sample pyJoules-style CSV file and return its path."""
    csv_file = tmp_path / "energy.csv"
    csv_file.write_text(
        "timestamp;tag;duration;package_0;dram_0\n"
        "1000;test_a;0.5;10.0;2.0\n"
        "1001;test_b;0.6;12.0;3.0\n"
    )
    return str(csv_file)


# ── init_db ──────────────────────────────────────────────────────────────


class TestInitDb:
    def test_creates_tables(self, db_path):
        """Tables are created after init_db."""
        import sqlite3

        conn = sqlite3.connect(db_path)
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = sorted(row[0] for row in cur.fetchall())
        conn.close()
        assert "module_energy_stats" in tables
        assert "testcase_energy" in tables
        assert "testcase_module_map" in tables

    def test_idempotent(self, db_path):
        """Calling init_db twice does not raise."""
        init_db(db_path)


# ── load_testcase_energy_csv ─────────────────────────────────────────────


class TestLoadTestcaseEnergyCsv:
    def test_load_rows(self, db_path, sample_csv):
        count = load_testcase_energy_csv("proj", sample_csv, db_path)
        assert count == 2

    def test_query_after_load(self, db_path, sample_csv):
        load_testcase_energy_csv("proj", sample_csv, db_path)
        rows = get_testcase_energies("proj", db_path)
        assert len(rows) == 2
        names = {r["test_name"] for r in rows}
        assert names == {"test_a", "test_b"}

    def test_fields(self, db_path, sample_csv):
        load_testcase_energy_csv("proj", sample_csv, db_path)
        rows = get_testcase_energies("proj", db_path)
        row_a = next(r for r in rows if r["test_name"] == "test_a")
        assert row_a["duration"] == pytest.approx(0.5)
        assert row_a["package_energy"] == pytest.approx(10.0)
        assert row_a["dram_energy"] == pytest.approx(2.0)

    def test_upsert(self, db_path, sample_csv):
        """Loading the same CSV twice does not duplicate rows."""
        load_testcase_energy_csv("proj", sample_csv, db_path)
        load_testcase_energy_csv("proj", sample_csv, db_path)
        rows = get_testcase_energies("proj", db_path)
        assert len(rows) == 2

    def test_project_isolation(self, db_path, sample_csv):
        load_testcase_energy_csv("alpha", sample_csv, db_path)
        load_testcase_energy_csv("beta", sample_csv, db_path)
        assert len(get_testcase_energies("alpha", db_path)) == 2
        assert len(get_testcase_energies("beta", db_path)) == 2


# ── save / get testcase_module_map ───────────────────────────────────────


class TestTestcaseModuleMap:
    def test_save_and_get(self, db_path):
        mappings = [
            {"test_name": "test_a", "module": "mod1"},
            {"test_name": "test_b", "module": "mod2"},
        ]
        count = save_testcase_module_map("proj", mappings, db_path)
        assert count == 2
        result = get_testcase_module_map("proj", db_path)
        assert len(result) == 2

    def test_upsert(self, db_path):
        mappings = [{"test_name": "test_a", "module": "mod1"}]
        save_testcase_module_map("proj", mappings, db_path)
        save_testcase_module_map("proj", mappings, db_path)
        assert len(get_testcase_module_map("proj", db_path)) == 1


# ── save / get module_energy_stats ───────────────────────────────────────


class TestModuleEnergyStats:
    SAMPLE_STATS = [
        {
            "module": "mod1",
            "mean": 45.23,
            "median": 42.10,
            "variance": 156.34,
            "best_case": 30.45,
            "worst_case": 78.92,
        },
        {
            "module": "mod2",
            "mean": 12.00,
            "median": 11.50,
            "variance": 5.20,
            "best_case": 9.00,
            "worst_case": 15.00,
        },
    ]

    def test_save_and_get(self, db_path):
        count = save_module_energy_stats("proj", self.SAMPLE_STATS, db_path)
        assert count == 2
        result = get_module_energy_stats("proj", db_path)
        assert len(result) == 2
        mod1 = next(r for r in result if r["module"] == "mod1")
        assert mod1["mean"] == pytest.approx(45.23)
        assert mod1["median"] == pytest.approx(42.10)
        assert mod1["variance"] == pytest.approx(156.34)
        assert mod1["best_case"] == pytest.approx(30.45)
        assert mod1["worst_case"] == pytest.approx(78.92)

    def test_upsert_overwrites(self, db_path):
        save_module_energy_stats("proj", self.SAMPLE_STATS, db_path)
        updated = [{"module": "mod1", "mean": 99.0, "median": 99.0,
                     "variance": 0.0, "best_case": 99.0, "worst_case": 99.0}]
        save_module_energy_stats("proj", updated, db_path)
        result = get_module_energy_stats("proj", db_path)
        mod1 = next(r for r in result if r["module"] == "mod1")
        assert mod1["mean"] == pytest.approx(99.0)

    def test_empty_project(self, db_path):
        result = get_module_energy_stats("nonexistent", db_path)
        assert result == []

    def test_project_isolation(self, db_path):
        save_module_energy_stats("alpha", self.SAMPLE_STATS, db_path)
        assert len(get_module_energy_stats("alpha", db_path)) == 2
        assert len(get_module_energy_stats("beta", db_path)) == 0
