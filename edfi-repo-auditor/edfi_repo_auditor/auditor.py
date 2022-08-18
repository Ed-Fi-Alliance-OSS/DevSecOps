# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import ast
import json
import logging
import time

from edfi_repo_auditor.config import Configuration
from edfi_repo_auditor.github_client import GitHubClient
from datetime import datetime, timedelta


logger: logging.Logger = logging.getLogger(__name__)


def run_audit(config: Configuration) -> None:
    start = time.time()
    client = GitHubClient(config.personal_access_token)

    repositories = config.repositories if config.repositories != [] else client.get_repositories(config.organization)

    report = {}
    for repo in repositories:
        repo_config = get_repo_information(client, repo, config.organization)
        logger.debug(f"Repo configuration: {repo_config}")
        actions = audit_actions(client, repo, config.organization)
        logger.debug(f"Actions {actions}")
        file_review = review_files(client, repo, config.organization)
        logger.debug(f"Files: {file_review}")

        checklist = actions | file_review | repo_config
        auditing_rules = get_file()
        score = get_result(checklist, auditing_rules["rules"])
        logger.debug(f"Rules to follow: {auditing_rules}")

        report[repo] = {
            "score": score,
            "result": "OK" if score > auditing_rules["threshold"] else "Action required",
            "description": checklist
        }

    if config.save_results is True:
        json_report = json.dumps(report, indent=4)

        with open("reports/audit-result.json", "w") as outfile:
            outfile.write(json_report)
    else:
        # Using print instead of logger to get result in JSON format
        print(report)

    logger.info(f"Finished auditing repositories for {config.organization} in {'{:.2f}'.format(time.time() - start)} seconds")


def audit_actions(client: GitHubClient, repository: str, organization: str) -> dict:
    audit_results = {
        'Has Actions': False,
        'Uses CodeQL': False,
        'Uses Allowed list': False
    }

    actions = client.get_actions(organization, repository)

    logger.debug(f"Got {actions['total_count']} workflow files")

    audit_results['Has Actions'] = actions['total_count'] > 0

    workflow_paths = [actions['workflows']['path'] for actions['workflows'] in actions['workflows']]
    for file_path in workflow_paths:
        file_content = client.get_file_content(organization, repository, file_path)
        if not file_content:
            logger.debug("File not found")
            continue

        if not audit_results['Uses CodeQL']:
            audit_results['Uses CodeQL'] = "uses: github/codeql-action/analyze" in file_content

        if not audit_results['Uses Allowed list']:
            audit_results['Uses Allowed list'] = "uses: ed-fi-alliance-oss/ed-fi-actions/.github/workflows/repository-scanner.yml" in file_content

    return audit_results


def get_repo_information(client: GitHubClient, repository: str, organization: str) -> dict:
    information = client.get_repository_information(organization, repository)

    # Currently,this is only checking if there are alerts, which does not differentiates if dependabot is enabled or not
    vulnerabilities = [alerts for alerts in information["vulnerabilityAlerts"]["nodes"]
                       if (alerts["createdAt"] < (datetime.now() - timedelta(3 * 7)).isoformat() and
                       alerts["securityVulnerability"]["advisory"]["severity"] in ['CRITICAL', 'HIGH'])]

    rulesForMain = [rules for rules in information["branchProtectionRules"]["nodes"] if rules["pattern"] == "main"]
    rules = rulesForMain[0] if rulesForMain else None

    logger.debug(f"Repository information: {information}")

    return {
        "Requires Signed commits": rules["requiresCommitSignatures"] if rules else False,
        "Requires Code review": rules["requiresApprovingReviews"] if rules else False,
        "Requires PR": (rules["requiresApprovingReviews"] and rules["isAdminEnforced"]) if rules else False,
        "Has Wiki Enabled": information["hasWikiEnabled"],
        "Has Issues Enabled": information["hasIssuesEnabled"],
        "Has Projects Enabled": information["hasProjectsEnabled"],
        "Has Discussions": information["discussions"]["totalCount"] > 0,
        "Deletes head branch": information["deleteBranchOnMerge"],
        "Uses Squash Merge": information["squashMergeAllowed"],
        "Has License Information": information["licenseInfo"] is not None,
        'Has Dependabot alerts': len(vulnerabilities) > 0
    }


def review_files(client: GitHubClient, repository: str, organization: str) -> dict:
    files = {
        "README.md": False,
        "CONTRIBUTORS.md": False,
        "NOTICES.md": False,
        "LICENSE": False
    }

    for file in files:
        file_content = client.get_file_content(organization, repository, file)
        if file_content:
            files[file] = True

    return files


def get_result(checklist: dict, rules: dict) -> int:
    score = 0
    for property in rules:
        try:
            if (checklist[property] is True):
                score += rules[property]
        except KeyError:
            logger.error(f"Unable to read property {property} in results")

    return score


def get_file() -> dict:
    with open("scoring.json", "r") as file:
        return ast.literal_eval(file.read())
