# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from collections import namedtuple

DEFAULT_SUCCESS_MESSAGE = "OK"

options = namedtuple("checklist", [
                      "HAS_ACTIONS",
                      "CODEQL",
                      "APPROVED_ACTIONS",
                      "TEST_REPORTER",
                      "UNIT_TESTS",
                      "LINTER",
                      "SIGNED_COMMITS",
                      "CODE_REVIEW",
                      "REQUIRES_PR",
                      "ADMIN_PR",
                      "WIKI",
                      "ISSUES",
                      "PROJECTS",
                      "DISCUSSIONS",
                      "DELETES_HEAD",
                      "USES_SQUASH",
                      "LICENSE_INFORMATION",
                      "DEPENDABOT_ENABLED",
                      "DEPENDABOT_ALERTS",
                      "README",
                      "CONTRIBUTORS",
                      "NOTICES",
                      "LICENSE"
                    ])

CHECKLIST = options(
              HAS_ACTIONS={
                "description": "Has Actions",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Repo is not using GH Actions"
              },
              CODEQL={
                "description": "Uses CodeQL",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "CodeQL not found"
              },
              APPROVED_ACTIONS={
                "description": "Uses only approved GitHub Actions",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Consider using only approved GH Actions"
              },
              TEST_REPORTER={
                "description": "Uses Test Reporter",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Not found"
              },
              UNIT_TESTS={
                "description": "Has Unit Tests",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Not found"
              },
              LINTER={
                "description": "Has Linter",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Linting step not found"
              },
              SIGNED_COMMITS={
                "description": "Requires Signed commits",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Commits should be signed"
              },
              CODE_REVIEW={
                "description": "Requires Code review",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Code review not required"
              },
              REQUIRES_PR={
                "description": "Requires PR",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Can push without PR"
              },
              ADMIN_PR={
                "description": "Admin cannot bypass PR",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Admin can bypass"
              },
              WIKI={
                "description": "Wiki Disabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "WARNING: Wiki is enabled"
              },
              ISSUES={
                "description": "Issues Disabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "WARNING: Issues are enabled"
              },
              PROJECTS={
                "description": "Projects Disabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "WARNING: Projects are enabled"
              },
              DISCUSSIONS={
                "description": "Discussions Disabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "WARNING: Discussions are enabled"
              },
              DELETES_HEAD={
                "description": "Deletes head branch",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Branch should be deleted on merge"
              },
              USES_SQUASH={
                "description": "Uses Squash Merge",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Should use squash merges"
              },
              LICENSE_INFORMATION={
                "description": "License Information",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "License not found"
              },
              DEPENDABOT_ENABLED={
                "description": "Dependabot Enabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "Dependabot is not enabled"
              },
              DEPENDABOT_ALERTS={
                "description": "Dependabot Alerts",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "WARNING: Review existing alerts and dependabot status"
              },
              README={
                "description": "Has README",
                "filename": ["README.md"],
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "File not found"
              },
              CONTRIBUTORS={
                "description": "Has CONTRIBUTORS",
                "filename": ["CONTRIBUTORS.md"],
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "File not found"
              },
              NOTICES={
                "description": "Has NOTICES",
                "filename": ["NOTICES.md"],
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "File not found"
              },
              LICENSE={
                "description": "Has LICENSE",
                "filename": ["LICENSE.txt", "LICENSE"],
                "success": DEFAULT_SUCCESS_MESSAGE,
                "fail": "LICENSE or LICENSE.txt file not found"
              })


def get_message(property: str, flag: bool) -> str:
    return property["success"] if flag else property["fail"]
