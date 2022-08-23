# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from collections import namedtuple

options = namedtuple("checklist",
                     ["HAS_ACTIONS",
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
                      "DEPENDABOT_HAS_ALERTS",
                      "README",
                      "CONTRIBUTORS",
                      "NOTICES",
                      "LICENSE"])

CHECKLIST = options(
              HAS_ACTIONS="Has Actions",
              CODEQL="Uses CodeQL",
              APPROVED_ACTIONS="Uses only approved GitHub Actions",
              TEST_REPORTER="Uses Test Reporter",
              UNIT_TESTS="Has Unit Tests",
              LINTER="Has Linter",
              SIGNED_COMMITS="Requires Signed commits",
              CODE_REVIEW="Requires Code review",
              REQUIRES_PR="Requires PR",
              ADMIN_PR="Admin cannot bypass PR",
              WIKI="Has Wiki Enabled",
              ISSUES="Has Issues Enabled",
              PROJECTS="Has Projects Enabled",
              DISCUSSIONS="Has Discussions",
              DELETES_HEAD="Deletes head branch",
              USES_SQUASH="Uses Squash Merge",
              LICENSE_INFORMATION="Has License Information",
              DEPENDABOT_HAS_ALERTS="Has Dependabot alerts",
              README="README.md",
              CONTRIBUTORS="CONTRIBUTORS.md",
              NOTICES="NOTICES.md",
              LICENSE="LICENSE"
              )
