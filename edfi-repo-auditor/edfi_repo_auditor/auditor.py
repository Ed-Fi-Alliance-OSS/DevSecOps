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
        actions = audit_actions(client, repo, config)

        report[repo] = {'dependabot alerts': alert_count, 'has_actions': actions['has_actions'], 'has_codeql': actions['has_codeql']}

    logger.info(report)

    if config.save_results == True:
        json_report = json.dumps(report, indent=4)

        with open(f"reports/audit-result.json", "w") as outfile:
            outfile.write(json_report)

def audit_actions(client: GitHubClient, repository: str, config: Configuration) -> dict:
    actions = client.get_actions(config.organization, repository)

    workflow_paths = [actions['workflows']['path'] for actions['workflows'] in actions['workflows']]
    found_codeql = False
    for file_path in workflow_paths:
        file_content = client.get_file_content(config.organization, repository, file_path)
        found_codeql = "uses: github/codeql-action/analyze" in file_content
        if found_codeql:
            break

    return { 'has_actions': actions['total_count'] > 0, 'has_codeql': found_codeql }

