# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import math
from pathlib import Path

import pandas as pd
import pytest

from edfi_tech_metrics.ossf_score import compare_with_previous_scores


def test_no_previous_files_prints_message(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    current = {"org/repo-a": 8.5}
    compare_with_previous_scores(current, str(tmp_path))
    captured = capsys.readouterr()
    assert "No previous scores" in captured.out


def test_no_previous_files_returns_current_df_and_empty_lists(tmp_path: Path) -> None:
    current = {"org/repo-a": 8.5}
    result_df, improved, worsened = compare_with_previous_scores(current, str(tmp_path))
    assert list(result_df["Current Score"]) == [8.5]
    assert improved == []
    assert worsened == []


def test_with_previous_file_calculates_score_difference(tmp_path: Path) -> None:
    pd.DataFrame([{"Repository": "org/repo-a", "Score": 7.0}]).to_csv(
        tmp_path / "2025-01-01.csv", index=False
    )
    current = {"org/repo-a": 8.5}
    result_df, _, _ = compare_with_previous_scores(current, str(tmp_path))
    row = result_df[result_df["Repository"] == "org/repo-a"].iloc[0]
    assert row["Current Score"] == pytest.approx(8.5)
    assert row["Previous Score"] == pytest.approx(7.0)
    assert row["Score Difference"] == pytest.approx(1.5)


def test_improved_ten_percent_in_improved_list(tmp_path: Path) -> None:
    pd.DataFrame([{"Repository": "org/repo-a", "Score": 7.0}]).to_csv(
        tmp_path / "2025-01-01.csv", index=False
    )
    current = {"org/repo-a": 7.7}  # exactly +10%
    _, improved, worsened = compare_with_previous_scores(current, str(tmp_path))
    assert "org/repo-a" in improved
    assert "org/repo-a" not in worsened


def test_worsened_ten_percent_in_worsened_list(tmp_path: Path) -> None:
    pd.DataFrame([{"Repository": "org/repo-a", "Score": 7.0}]).to_csv(
        tmp_path / "2025-01-01.csv", index=False
    )
    current = {"org/repo-a": 6.3}  # exactly -10%
    _, improved, worsened = compare_with_previous_scores(current, str(tmp_path))
    assert "org/repo-a" in worsened
    assert "org/repo-a" not in improved


def test_small_change_in_neither_list(tmp_path: Path) -> None:
    pd.DataFrame([{"Repository": "org/repo-a", "Score": 7.0}]).to_csv(
        tmp_path / "2025-01-01.csv", index=False
    )
    current = {"org/repo-a": 7.5}  # ~7.1%, below threshold
    _, improved, worsened = compare_with_previous_scores(current, str(tmp_path))
    assert "org/repo-a" not in improved
    assert "org/repo-a" not in worsened


def test_repo_only_in_current_has_nan_previous_score(tmp_path: Path) -> None:
    pd.DataFrame([{"Repository": "org/repo-b", "Score": 7.0}]).to_csv(
        tmp_path / "2025-01-01.csv", index=False
    )
    current = {"org/repo-a": 8.5}  # different repo than in previous file
    result_df, _, _ = compare_with_previous_scores(current, str(tmp_path))
    row = result_df[result_df["Repository"] == "org/repo-a"].iloc[0]
    assert math.isnan(row["Previous Score"])
