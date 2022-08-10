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
        branch_protection = get_branch_protection_info(client, repo, config)
        logger.debug(f"Branch protection {branch_protection}")
        actions = audit_actions(client, repo, config)
        logger.debug(f"Actions {actions}")

        if actions:
            actions['Dependabot alerts'] = alert_count

        report[repo] = actions | branch_protection

    if config.save_results == True:
        json_report = json.dumps(report, indent=4)

        with open(f"reports/audit-result.json", "w") as outfile:
            outfile.write(json_report)
    else:
        #Using print instead of logger to get result in JSON format
        print(report)

    logger.info(f"Finished auditing repositories for {config.organization} in {'{:.2f}'.format(time.time() - start)} seconds")

def audit_actions(client: GitHubClient, repository: str, config: Configuration) -> dict:
    audit_results = {
        'Actions': False,
        'CodeQL': False,
        'Allowed list': False
    }

    actions = client.get_actions(config.organization, repository)

    logger.debug(f"Got {actions['total_count']} workflow files")

    audit_results['Actions'] = actions['total_count'] > 0

    workflow_paths = [actions['workflows']['path'] for actions['workflows'] in actions['workflows']]
    for file_path in workflow_paths:
        file_content = client.get_file_content(config.organization, repository, file_path)
        if not file_content:
            logger.debug("File not found")
            continue

        if not audit_results['CodeQL']:
            audit_results['CodeQL'] = "uses: github/codeql-action/analyze" in file_content

        if not audit_results['Allowed list']:
            audit_results['Allowed list'] = "uses: ed-fi-alliance-oss/ed-fi-actions/.github/workflows/repository-scanner.yml" in file_content

    return audit_results

def get_branch_protection_info(client: GitHubClient, repository: str, config: Configuration) -> dict:
    allRules = client.get_protection_rules(config.organization, repository)

    rulesForMain = [allRules for allRules in allRules if allRules["pattern"] == "main"]
    rules = rulesForMain[0] if rulesForMain else None

    logger.debug(f"Rules for main: {rules}")

    return {
        "Signed commits": rules["requiresCommitSignatures"] if rules else False,
        "Code review": rules["requiresApprovingReviews"] if rules else False,
        "Requires PR": (rules["requiresApprovingReviews"] and rules["isAdminEnforced"]) if rules else False
    }


