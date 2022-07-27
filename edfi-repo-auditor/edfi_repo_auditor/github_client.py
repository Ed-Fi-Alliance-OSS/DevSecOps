# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
from typing import List
from json import dumps

import pandas as pd
import requests
from requests import Response

from edfi_repo_auditor.log_helper import http_error

API_URL = "https://api.github.com"
GRAPHQL_ENDPOINT = f"{API_URL}/graphql"

REPO_TOKEN = "[REPOSITORY]"
ORG_TOKEN = "[OWNER]"

# Note that this doesn't handle paging and thus will not be sufficient if there
# are more than 100 alerts.
DEPENDABOT_ALERTS_TEMPLATE = """
{
  repository(name: "[REPOSITORY]", owner: "[OWNER]") {
    vulnerabilityAlerts(first: 100, states: [OPEN]) {
      nodes {
        createdAt
        dismissedAt
        securityVulnerability {
          package {
            name
          }
          advisory {
            description
            severity
          }
        }
      }
    }
  }
}
""".strip()

# Note that this doesn't handle paging and thus will not be sufficient if there
# are more than 100 repositories.
REPOSITORIES_TEMPLATE = """
{
  organization(login: "[OWNER]") {
    id
    repositories(first: 100) {
      nodes {
        name
      }
    }
  }
}
""".strip()

logger: logging.Logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, access_token: str):
        if len(access_token.strip()) == 0:
            raise ValueError("access_token cannot be blank")
        self.access_token = access_token

    def _execute_api_call(self, description: str, method: str, url: str, payload: str = None) -> dict:
        headers = {
            "Authorization": f"bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        logger.info(f"{description}")

        response: Response = requests.request(
            method, url, headers=headers, data=payload
        )

        if response.status_code == requests.codes.ok:
            body = response.json()

            # GitHub API will return 200 with error messages if the query is malformed.
            if "errors" in body:
                msg = f"Query for {description}."
                raise http_error(msg, response)

            return body
        else:
            msg = f"Executing {description}."
            raise http_error(msg, response)

    def _execute_graphql(self, description: str, query: str) -> dict:
        payload = dumps({"query": query, "variables": {}})

        body = self._execute_api_call(
            f"Querying for {description}", "POST", f"{GRAPHQL_ENDPOINT}", payload
        )

        return body

    def get_repositories(self, owner: str) -> List[str]:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")

        query = REPOSITORIES_TEMPLATE.replace(ORG_TOKEN, owner)
        body = self._execute_graphql(f"repositories for {owner}", query)

        df = pd.DataFrame(body["data"]["organization"]["repositories"]["nodes"])
        return df["name"].to_list()

    def get_dependabot_alert_count(self, owner: str, repository: str) -> int:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        query = DEPENDABOT_ALERTS_TEMPLATE.replace(ORG_TOKEN, owner).replace(
            REPO_TOKEN, repository
        )

        body = self._execute_graphql(
            f"dependabot alerts for {owner}/{repository}", query
        )

        return len(body["data"]["repository"]["vulnerabilityAlerts"]["nodes"])

    def get_actions(self, owner: str, repository: str):
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        body = self._execute_api_call(
            f"Getting actions for {owner}/{repository}", "GET", f"{API_URL}/repos/{owner}/{repository}/actions/workflows"
        )

        total_actions = body['total_count']

        logger.info(f"{owner}/{repository} has {total_actions} actions")


