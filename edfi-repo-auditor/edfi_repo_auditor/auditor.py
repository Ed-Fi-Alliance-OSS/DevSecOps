# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import logging
import time

from edfi_repo_auditor.config import Configuration
from edfi_repo_auditor.github_client import GitHubClient


logger: logging.Logger = logging.getLogger(__name__)


def run_audit(config: Configuration) -> None:
    start = time.time()
    client = GitHubClient(config.personal_access_token)

    repositories = config.repositories if config.repositories != [] else client.get_repositories(config.organization)

    report = {}
    for repo in repositories:
        alert_count = client.get_dependabot_alert_count(config.organization, repo)
        logger.debug(f"Got {alert_count} dependabot alerts")
        actions = audit_actions(client, repo, config)
        logger.debug(f"Actions {actions}")

        if actions:
            actions['Dependabot alerts'] = alert_count

        report[repo] = actions

    if config.save_results == True:
        json_report = json.dumps(report, indent=4)

        with open(f"reports/audit-result.json", "w") as outfile:
            outfile.write(json_report)
    else:
        print(report)

    logger.info(f"Finished auditing repositories for {config.organization} in {'{:.2f}'.format(time.time() - start)} seconds")

def audit_actions(client: GitHubClient, repository: str, config: Configuration) -> dict:
    actions = client.get_actions(config.organization, repository)

    logger.debug(f"Got {actions['total_count']} workflow files")

    results = { 'Has actions': actions['total_count'] > 0 }
    workflow_paths = [actions['workflows']['path'] for actions['workflows'] in actions['workflows']]

    found_codeql = False
    found_allowed = False

    for file_path in workflow_paths:
        file_content = client.get_file_content(config.organization, repository, file_path)
        if not file_content:
            logger.debug("File not found")
            continue

        if not found_codeql:
            found_codeql = "uses: github/codeql-action/analyze" in file_content

        if not found_allowed:
            found_allowed = not found_allowed or "uses: ed-fi-alliance-oss/ed-fi-actions/.github/workflows/repository-scanner.yml" in file_content

    results['Has codeql'] = found_codeql
    results['Has allowed list'] = found_allowed

    return results

