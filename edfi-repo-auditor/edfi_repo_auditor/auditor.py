# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import logging
import os
import re
import time
from typing import List
from edfi_repo_auditor.checklist import CHECKLIST

from edfi_repo_auditor.config import Configuration
from edfi_repo_auditor.github_client import GitHubClient
from datetime import datetime, timedelta
from pprint import pformat


logger: logging.Logger = logging.getLogger(__name__)

# Parameters to evaluate dependabot alerts
ALERTS_INCLUDED_SEVERITIES = ["CRITICAL", "HIGH"]
ALERTS_WEEKS_SINCE_CREATED = 3


def run_audit(config: Configuration) -> None:
    start = time.time()
    client = GitHubClient(config.personal_access_token)

    repositories = config.repositories if len(config.repositories) > 0 else client.get_repositories(config.organization)

    report: dict = {}
    for repo in repositories:
        logger.info(f"Scanning repository {repo}")
        repo_config = get_repo_information(client, config.organization, repo)
        logger.debug(f"Repo configuration: {repo_config}")
        actions = audit_actions(client, config.organization, repo)
        logger.debug(f"Actions {actions}")
        file_review = review_files(client, config.organization, repo)
        logger.debug(f"Files: {file_review}")

        results = set_audit_results(actions | file_review | repo_config)
        auditing_rules = get_file()
        score = 0  # get_result(results, auditing_rules["rules"])
        logger.debug(f"Rules to follow: {auditing_rules}")

        report[repo] = {
            "score": score,
            "result": "OK" if score > auditing_rules["threshold"] else "Action required",
            "description": results
        }

    if config.save_results is True:
        save_to_file(report, config.file_name)
    else:
        logger.info(pformat(report))

    logger.info(f"Finished auditing repositories for {config.organization} in {'{:.2f}'.format(time.time() - start)} seconds")


def set_audit_results(results: dict) -> dict:
    for property in CHECKLIST:
        print(property)

    return results


def audit_actions(client: GitHubClient, organization: str, repository: str) -> dict:
    audit_results = {
        CHECKLIST.HAS_ACTIONS: False,
        CHECKLIST.CODEQL: False,
        CHECKLIST.APPROVED_ACTIONS: False,
        CHECKLIST.TEST_REPORTER: False,
        CHECKLIST.UNIT_TESTS: False,
        CHECKLIST.LINTER: False
    }

    actions = client.get_actions(organization, repository)

    logger.debug(f"Got {actions['total_count']} workflow files")

    audit_results[CHECKLIST.HAS_ACTIONS] = actions["total_count"] > 0

    workflow_paths = [actions["workflows"]["path"] for actions["workflows"] in actions["workflows"]]
    for file_path in workflow_paths:
        file_content = client.get_file_content(organization, repository, file_path)
        if not file_content:
            logger.debug("File not found")
            continue

        if not audit_results[CHECKLIST.CODEQL]:
            audit_results[CHECKLIST.CODEQL] = "uses: github/codeql-action/analyze" in file_content

        if not audit_results[CHECKLIST.APPROVED_ACTIONS]:
            audit_results[CHECKLIST.APPROVED_ACTIONS] = "uses: ed-fi-alliance-oss/ed-fi-actions/.github/workflows/repository-scanner.yml" in file_content

        if not audit_results[CHECKLIST.TEST_REPORTER]:
            audit_results[CHECKLIST.TEST_REPORTER] = "uses: dorny/test-reporter" in file_content

        if not audit_results[CHECKLIST.UNIT_TESTS]:
            pattern = re.compile(r"unit.{0,2}test(s)?", flags=re.IGNORECASE)
            audit_results[CHECKLIST.UNIT_TESTS] = True if pattern.search(file_content) else False

        if not audit_results[CHECKLIST.LINTER]:
            pattern = re.compile(r"lint(er)?(s)?(ing)?", flags=re.IGNORECASE)
            audit_results[CHECKLIST.LINTER] = True if pattern.search(file_content) else False

    return audit_results


def get_repo_information(client: GitHubClient, organization: str, repository: str) -> dict:
    information = client.get_repository_information(organization, repository)

    dependabot = audit_alerts(client, organization, repository,
                              information["vulnerabilityAlerts"]["nodes"])

    rulesForMain = [rules for rules in information["branchProtectionRules"]["nodes"] if rules["pattern"] == "main"]
    rules = rulesForMain[0] if rulesForMain else None

    logger.debug(f"Repository information: {information}")

    return {
        CHECKLIST.SIGNED_COMMITS: rules["requiresCommitSignatures"] if rules else False,
        CHECKLIST.CODE_REVIEW: rules["requiresApprovingReviews"] if rules else False,
        CHECKLIST.REQUIRES_PR: rules["requiresApprovingReviews"] if rules else False,
        CHECKLIST.ADMIN_PR: (rules["isAdminEnforced"] is False) if rules else False,
        CHECKLIST.WIKI: information["hasWikiEnabled"],
        CHECKLIST.ISSUES: information["hasIssuesEnabled"],
        CHECKLIST.PROJECTS: information["hasProjectsEnabled"],
        CHECKLIST.DISCUSSIONS: information["discussions"]["totalCount"] > 0,
        CHECKLIST.DELETES_HEAD: information["deleteBranchOnMerge"],
        CHECKLIST.USES_SQUASH: information["squashMergeAllowed"],
        CHECKLIST.LICENSE_INFORMATION: information["licenseInfo"] is not None,
    } | dependabot


def audit_alerts(client: GitHubClient, organization: str, repository: str, alerts: List[str]) -> dict:
    vulnerabilities = [alerts for alerts in alerts
                       if (alerts["createdAt"] < (datetime.now() - timedelta(ALERTS_WEEKS_SINCE_CREATED * 7)).isoformat() and
                           alerts["securityVulnerability"]["advisory"]["severity"] in ALERTS_INCLUDED_SEVERITIES)]
    total_vulnerabilities = len(vulnerabilities)

    dependabot_enabled = client.has_dependabot_enabled(organization, repository)
    # ToDo: Get messages on success from a constant
    return {
        CHECKLIST.DEPENDABOT_ENABLED: "OK" if dependabot_enabled else "Dependabot is not enabled or given token does not have admin permission",
        CHECKLIST.DEPENDABOT_ALERTS: "OK" if dependabot_enabled and total_vulnerabilities == 0 else "Review existing alerts and dependabot status"
    }


def review_files(client: GitHubClient, organization: str, repository: str) -> dict:
    files = {
        CHECKLIST.README: False,
        CHECKLIST.CONTRIBUTORS: False,
        CHECKLIST.NOTICES: False,
        CHECKLIST.LICENSE: False
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


def save_to_file(report: dict, file_name: str) -> None:
    folder_name = "reports"

    path: str = None
    if file_name:
        _, ext = os.path.splitext(file_name)
        if (not ext) or (ext != '.json'):
            file_name += '.json'
        path = f"{folder_name}/{file_name}"
    else:
        path = f"{folder_name}/audit-result.json"

    logger.info(f"Saving report to {path}")
    json_report = json.dumps(report, indent=4)

    if not os.path.exists(f"{folder_name}/"):
        os.mkdir(folder_name)

    with open(path, "w") as outfile:
        outfile.write(json_report)


def get_file() -> dict:
    with open("scoring.json", "r") as file:
        return json.loads(file.read())
