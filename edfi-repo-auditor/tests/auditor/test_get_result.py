# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_repo_auditor.auditor import get_result


def describe_when_getting_results() -> None:
    def describe_given_no_rules() -> None:
        CHECKLIST = {
            "Has Actions": 5,
            "Uses Allowed list": 5,
            "README.md": 3
        }

        @pytest.fixture
        def results() -> int:
            return get_result(CHECKLIST, {})

        def it_returns_0(results: int) -> None:
            assert results == 0

    def describe_given_property_not_in_checklist() -> None:
        CHECKLIST = {
            "Uses Allowed list": False,
            "README.md": True
        }

        RULES = {
            "Has Actions": 5,
            "Uses Allowed list": 5,
            "README.md": 3
        }

        @pytest.fixture
        def results() -> int:
            return get_result(CHECKLIST, RULES)

        def it_adds_the_existing_properties(results: int) -> None:
            assert results == 3

    def describe_given_values_are_present() -> None:
        CHECKLIST = {
            "Has Actions": True,
            "Uses Allowed list": False,
            "README.md": True
        }

        RULES = {
            "Has Actions": 5,
            "Uses Allowed list": 5,
            "README.md": 3
        }

        @pytest.fixture
        def results() -> int:
            return get_result(CHECKLIST, RULES)

        def it_adds_the_properties(results: int) -> None:
            assert results == 8
