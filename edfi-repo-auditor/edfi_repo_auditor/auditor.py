# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import logging

from edfi_repo_auditor.config import Configuration
from edfi_repo_auditor.github_client import GitHubClient


logger: logging.Logger = logging.getLogger(__name__)


def run_audit(config: Configuration) -> None:
    client = GitHubClient(config.personal_access_token)

    repositories = config.repositories if config.repositories != [] else client.get_repositories(config.organization)

    report = {}
    for repo in repositories:
        alert_count = client.get_dependabot_alert_count(config.organization, repo)
        action_count = client.get_actions(config.organization, repo)

        report[repo] = {'dependabot alerts': alert_count, 'actions': action_count}

    logger.info(report)

    if config.save_results == True:
        json_report = json.dumps(report, indent=4)

        with open(f"reports/audit-result.json", "w") as outfile:
            outfile.write(json_report)

