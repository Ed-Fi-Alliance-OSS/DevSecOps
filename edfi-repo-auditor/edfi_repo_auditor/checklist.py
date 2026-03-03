# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from collections import namedtuple

CHECKLIST_DEFAULT_SUCCESS_MESSAGE = "✅ OK"

checklist = namedtuple(
    "checklist",
    [
        "HAS_ACTIONS",
        "APPROVED_ACTIONS",
        "TEST_REPORTER",
        "UNIT_TESTS",
        "CODEQL",
        "WIKI",
        "ISSUES",
        "PROJECTS",
        "DELETES_HEAD",
        "USES_SQUASH",
        "LICENSE_INFORMATION",
        "DEPENDABOT_ENABLED",
        "DEPENDABOT_ALERTS",
        "NOTICES",
        "CODE_OF_CONDUCT",
        "LICENSE",
        "CONTRIBUTORS",
        "SECURITY",
        "AGENTS",
        "REQUIRES_PULL_REQUEST",
        "ADMIN_CANNOT_BYPASS",
        "RESTRICTS_CREATION",
        "RESTRICTS_DELETION",
        "REQUIRES_LINEAR_HISTORY",
    ],
)

CHECKLIST = checklist(
    HAS_ACTIONS={"description": "Has Actions", "fail": "❌ FAILED: Repo is not using GH Actions"},
    APPROVED_ACTIONS={
        "description": "Uses only approved GitHub Actions",
        "fail": "❌ FAILED: No. Consider using only approved GH Actions",
    },
    TEST_REPORTER={"description": "Uses Test Reporter", "fail": "❌ FAILED: Not found"},
    UNIT_TESTS={"description": "Has Unit Tests", "fail": "❌ FAILED: Not found"},
    CODEQL={"description": "Uses CodeQL", "fail": "❌ FAILED: Not found"},
    WIKI={"description": "Wiki Disabled", "fail": "⚠️ WARNING: Wiki is enabled"},
    ISSUES={"description": "Issues Enabled", "fail": "⚠️ WARNING: Issues are not enabled"},
    PROJECTS={
        "description": "Projects Disabled",
        "fail": "⚠️ WARNING: Projects are enabled",
    },
    DELETES_HEAD={
        "description": "Deletes head branch",
        "fail": "❌ FAILED: Branch should be deleted on merge",
    },
    USES_SQUASH={
        "description": "Uses Squash Merge",
        "fail": "❌ FAILED: Should use squash merges",
    },
    LICENSE_INFORMATION={
        "description": "License Information",
        "fail": "❌ FAILED: License not found",
    },
    DEPENDABOT_ENABLED={
        "description": "Dependabot Enabled",
        "fail": "❌ FAILED: Dependabot is not enabled",
    },
    DEPENDABOT_ALERTS={
        "description": "Dependabot Alerts",
        "fail": "⚠️ WARNING: Review existing alerts and dependabot status",
    },
    CODE_OF_CONDUCT={
        "description": "Has CODE_OF_CONDUCT.md",
        "filename": "CODE_OF_CONDUCT.md",
        "fail": "⚠️ WARNING: File not found",
    },
    NOTICES={
        "description": "Has NOTICES.md",
        "filename": "NOTICES.md",
        "fail": "⚠️ WARNING: File not found",
    },
    LICENSE={
        "description": "Has LICENSE",
        "filename": "LICENSE",
        "fail": "⚠️ WARNING: File not found",
    },
    CONTRIBUTORS={
        "description": "Has CONTRIBUTORS.md",
        "filename": "CONTRIBUTORS.md",
        "fail": "⚠️ WARNING: File not found",
    },
    SECURITY={
        "description": "Has SECURITY.md",
        "filename": "SECURITY.md",
        "fail": "⚠️ WARNING: File not found",
    },
    AGENTS={
        "description": "Has AGENTS.md",
        "filename": "AGENTS.md",
        "fail": "⚠️ WARNING: File not found",
    },
    REQUIRES_PULL_REQUEST={
        "description": "Requires pull request",
        "fail": "❌ FAILED: Branch does not require a pull request",
    },
    ADMIN_CANNOT_BYPASS={
        "description": "Admin cannot bypass PR",
        "fail": "❌ FAILED: Admins can bypass branch protection",
    },
    RESTRICTS_CREATION={
        "description": "Restricts branch creation",
        "fail": "❌ FAILED: Branch creation is not restricted",
    },
    RESTRICTS_DELETION={
        "description": "Restricts deletion",
        "fail": "❌ FAILED: Branch deletion is not restricted",
    },
    REQUIRES_LINEAR_HISTORY={
        "description": "Requires linear history",
        "fail": "❌ FAILED: Linear history is not required",
    },)


def get_message(property: dict, flag: bool) -> str:
    return CHECKLIST_DEFAULT_SUCCESS_MESSAGE if flag else property["fail"]
