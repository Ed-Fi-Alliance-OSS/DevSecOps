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
                "error": ""
              },
              CODEQL={
                "description": "Uses CodeQL",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              APPROVED_ACTIONS={
                "description": "Uses only approved GitHub Actions",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              TEST_REPORTER={
                "description": "Uses Test Reporter",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              UNIT_TESTS={
                "description": "Has Unit Tests",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              LINTER={
                "description": "Has Linter",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              SIGNED_COMMITS={
                "description": "Requires Signed commits",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              CODE_REVIEW={
                "description": "Requires Code review",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              REQUIRES_PR={
                "description": "Requires PR",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              ADMIN_PR={
                "description": "Admin cannot bypass PR",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              WIKI={
                "description": "Has Wiki Enabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              ISSUES={
                "description": "Has Issues Enabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              PROJECTS={
                "description": "Has Projects Enabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              DISCUSSIONS={
                "description": "Has Discussions",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              DELETES_HEAD={
                "description": "Deletes head branch",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              USES_SQUASH={
                "description": "Uses Squash Merge",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              LICENSE_INFORMATION={
                "description": "License Information",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              DEPENDABOT_ENABLED={
                "description": "Dependabot Enabled",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": "Dependabot is not enabled or given token does not have admin permission"
              },
              DEPENDABOT_ALERTS={
                "description": "Dependabot Alerts",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": "Review existing alerts and dependabot status"
              },
              README={
                "description": "README.md",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              CONTRIBUTORS={
                "description": "CONTRIBUTORS.md",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              NOTICES={
                "description": "NOTICES.md",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              },
              LICENSE={
                "description": "LICENSE",
                "success": DEFAULT_SUCCESS_MESSAGE,
                "error": ""
              })
