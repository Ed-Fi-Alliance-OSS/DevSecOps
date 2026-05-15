# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pandas as pd
import pytest
from pathlib import Path

from edfi_tech_metrics.improvements import calculate_improvements


def _write_stats_csv(path: Path, date: str, rows: list) -> None:
    for row in rows:
        row["date"] = date
    pd.DataFrame(rows).to_csv(path, index=False)


def test_improvement_positive_delta(tmp_path: Path) -> None:
    _write_stats_csv(tmp_path / "2024-01-01.csv", "2024-01-01",
                     [{"project": "PROJ", "mean": 30.0}])
    _write_stats_csv(tmp_path / "2024-02-01.csv", "2024-02-01",
                     [{"project": "PROJ", "mean": 15.0}])
    result = calculate_improvements(str(tmp_path), [])
    row = result[result["project"] == "PROJ"].iloc[0]
    assert row["delta"] == pytest.approx(0.5)  # (30 - 15) / 30


def test_regression_negative_delta(tmp_path: Path) -> None:
    _write_stats_csv(tmp_path / "2024-01-01.csv", "2024-01-01",
                     [{"project": "PROJ", "mean": 15.0}])
    _write_stats_csv(tmp_path / "2024-02-01.csv", "2024-02-01",
                     [{"project": "PROJ", "mean": 30.0}])
    result = calculate_improvements(str(tmp_path), [])
    row = result[result["project"] == "PROJ"].iloc[0]
    assert row["delta"] == pytest.approx(-1.0)  # (15 - 30) / 15


def test_no_change_zero_delta(tmp_path: Path) -> None:
    _write_stats_csv(tmp_path / "2024-01-01.csv", "2024-01-01",
                     [{"project": "PROJ", "mean": 20.0}])
    _write_stats_csv(tmp_path / "2024-02-01.csv", "2024-02-01",
                     [{"project": "PROJ", "mean": 20.0}])
    result = calculate_improvements(str(tmp_path), [])
    row = result[result["project"] == "PROJ"].iloc[0]
    assert row["delta"] == pytest.approx(0.0)


def test_multiple_projects_get_separate_deltas(tmp_path: Path) -> None:
    _write_stats_csv(tmp_path / "2024-01-01.csv", "2024-01-01", [
        {"project": "PROJ-A", "mean": 40.0},
        {"project": "PROJ-B", "mean": 20.0},
    ])
    _write_stats_csv(tmp_path / "2024-02-01.csv", "2024-02-01", [
        {"project": "PROJ-A", "mean": 20.0},
        {"project": "PROJ-B", "mean": 10.0},
    ])
    result = calculate_improvements(str(tmp_path), [])
    assert result[result["project"] == "PROJ-A"].iloc[0]["delta"] == pytest.approx(0.5)
    assert result[result["project"] == "PROJ-B"].iloc[0]["delta"] == pytest.approx(0.5)


def test_data_spread_across_multiple_csv_files(tmp_path: Path) -> None:
    # Date 1 data split across two files
    _write_stats_csv(tmp_path / "2024-01-01-part1.csv", "2024-01-01",
                     [{"project": "PROJ-A", "mean": 40.0}])
    _write_stats_csv(tmp_path / "2024-01-01-part2.csv", "2024-01-01",
                     [{"project": "PROJ-B", "mean": 20.0}])
    # Date 2 in one file
    _write_stats_csv(tmp_path / "2024-02-01.csv", "2024-02-01", [
        {"project": "PROJ-A", "mean": 20.0},
        {"project": "PROJ-B", "mean": 10.0},
    ])
    result = calculate_improvements(str(tmp_path), [])
    assert len(result) == 2
    assert result[result["project"] == "PROJ-A"].iloc[0]["delta"] == pytest.approx(0.5)
    assert result[result["project"] == "PROJ-B"].iloc[0]["delta"] == pytest.approx(0.5)
