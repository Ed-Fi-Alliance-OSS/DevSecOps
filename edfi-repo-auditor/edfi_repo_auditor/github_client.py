# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
from datetime import datetime, timezone
from typing import List, Optional
from json import dumps

import base64
import pandas as pd
import requests
from requests import Response

from edfi_repo_auditor.log_helper import http_error

API_URL = "https://api.github.com"
GRAPHQL_ENDPOINT = f"{API_URL}/graphql"

# Note that this doesn't handle paging and thus will not be sufficient if there
# are more than 100 repositories.
REPOSITORIES_TEMPLATE = """
query($owner: String!) {
  organization(login: $owner) {
    id
    repositories(first: 100) {
      totalCount
      nodes {
        name
      }
    }
  }
}
""".strip()

# Note that this doesn't handle paging and thus will not be sufficient if there
# are more than 100 alerts.
REPOSITORY_INFORMATION_TEMPLATE = """
query($owner: String!, $repository: String!) {
  repository(name: $repository, owner: $owner) {
    vulnerabilityAlerts(first: 100, states: [OPEN]) {
      nodes {
        createdAt
        securityVulnerability {
          package {
            name
          }
          advisory {
            severity
          }
        }
      }
    }
    rulesets(first: 10) {
      nodes {
        bypassActors(first: 10) {
          edges {
            node {
              organizationAdmin
              actor {
                __typename
              }
            }
          }
        }
        conditions {
          refName {
            include
          }
        }
        enforcement
        name
        rules(first: 20) {
          nodes {
            type
          }
        }
        target
      }
    }
    hasWikiEnabled
    hasIssuesEnabled
    hasProjectsEnabled
    deleteBranchOnMerge
    squashMergeAllowed
    licenseInfo {
      key
    }
  }
}
""".strip()

PULL_REQUESTS_WITH_REVIEWS_TEMPLATE = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(
      first: 20
      states: [MERGED]
      orderBy: {field: CREATED_AT, direction: DESC}
      after: $cursor
    ) {
      nodes {
        number
        createdAt
        closedAt
        mergedAt
        author { login }
        additions
        deletions
        changedFiles
        reviews(first: 100) {
          pageInfo { hasNextPage }
          nodes {
            author { login }
            state
            submittedAt
          }
        }
      }
      pageInfo { hasNextPage endCursor }
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

    def _execute_api_call(
        self, description: str, method: str, url: str, payload: str = ""
    ) -> dict:
        headers = {
            "Authorization": f"bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        logger.debug(f"{description}")

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
        elif response.status_code == requests.codes.no_content:
            # There's a failure when attempting to convert a 204 response to JSON
            return {"status_code": response.status_code}
        else:
            msg = f"Query for {description}."
            raise http_error(msg, response)

    def _execute_graphql(self, description: str, query: str, variables: dict = {}) -> dict:
        payload = dumps({"query": query, "variables": variables})

        body = self._execute_api_call(
            f"Querying for {description}", "POST", f"{GRAPHQL_ENDPOINT}", payload
        )

        return body

    def get_repositories(self, owner: str) -> List[str]:
        logger.info(f"Getting all repositories for organization {owner}")
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")

        body = self._execute_graphql(
            f"repositories for {owner}",
            REPOSITORIES_TEMPLATE,
            {"owner": owner},
        )

        total_repos = body["data"]["organization"]["repositories"]["totalCount"]
        if total_repos > 100:
            logger.warning(
                f"There are over 100 repos in {owner}. Update the query to handle pagination"
            )

        df = pd.DataFrame(body["data"]["organization"]["repositories"]["nodes"])
        return df["name"].to_list()

    def get_actions(self, owner: str, repository: str) -> dict:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        actions = self._execute_api_call(
            f"Getting actions for {owner}/{repository}",
            "GET",
            f"{API_URL}/repos/{owner}/{repository}/actions/workflows",
        )
        return actions

    def get_repository_information(self, owner: str, repository: str) -> dict:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        body = self._execute_graphql(
            f"protection rules for {owner}/{repository}",
            REPOSITORY_INFORMATION_TEMPLATE,
            {"owner": owner, "repository": repository},
        )

        return body["data"]["repository"]

    def has_dependabot_enabled(self, owner: str, repository: str) -> bool:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        has_dependabot = False
        try:
            dependabot = self._execute_api_call(
                f"Detecting if Dependabot is enabled for {owner}/{repository}",
                "GET",
                f"{API_URL}/repos/{owner}/{repository}/vulnerability-alerts",
            )
            has_dependabot = dependabot["status_code"] == requests.codes.no_content
        except RuntimeError as e:
            logger.warning(
                f"Failed to detect Dependabot status for {owner}/{repository}: {e}"
            )
            has_dependabot = False

        return has_dependabot

    def get_file_content(self, owner: str, repository: str, path: str) -> Optional[str]:
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")
        if len(path.strip()) == 0:
            raise ValueError("path cannot be blank")

        file_result = None
        try:
            file_result = self._execute_api_call(
                f"Getting file {path} for {owner}/{repository}",
                "GET",
                f"{API_URL}/repos/{owner}/{repository}/contents/{path}",
            )
        except RuntimeError as e:
            logger.warning(f"Failed to get file {path} for {owner}/{repository}: {e}")

        return (
            base64.b64decode(file_result["content"]).decode("UTF-8")
            if file_result
            else None
        )

    def get_pull_requests(
        self, owner: str, repository: str, state: str = "closed", per_page: int = 100
    ) -> List[dict]:
        """
        Get pull requests with full pagination.

        Args:
            owner: Repository owner
            repository: Repository name
            state: PR state filter ('open', 'closed', or 'all')
            per_page: Results per page (max 100)

        Returns:
            List of PR records with number, created_at, closed_at, merged_at,
            user, additions, deletions, changed_files
        """
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        all_prs: List[dict] = []
        page = 1

        while True:
            logger.info(f"Getting pull requests for {owner}/{repository}, page {page}")
            url = (
                f"{API_URL}/repos/{owner}/{repository}/pulls"
                f"?state={state}&per_page={per_page}&page={page}"
            )

            prs = self._execute_api_call(
                f"Getting PRs for {owner}/{repository}",
                "GET",
                url,
            )

            if not prs:
                break

            for pr in prs:
                pr_record = {
                    "number": pr["number"],
                    "created_at": pr.get("created_at"),
                    "closed_at": pr.get("closed_at"),
                    "merged_at": pr.get("merged_at"),
                    "user": pr.get("user", {}).get("login"),
                    "additions": pr.get("additions"),
                    "deletions": pr.get("deletions"),
                    "changed_files": pr.get("changed_files"),
                }
                all_prs.append(pr_record)

            if len(prs) < per_page:
                break

            page += 1

        return all_prs

    def get_pull_request_detail(
        self, owner: str, repository: str, pr_number: int
    ) -> dict:
        """
        Get detailed information for a specific pull request.

        Args:
            owner: Repository owner
            repository: Repository name
            pr_number: Pull request number

        Returns:
            PR record with detailed fields including additions, deletions, changed_files
        """
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        url = f"{API_URL}/repos/{owner}/{repository}/pulls/{pr_number}"
        pr = self._execute_api_call(
            f"Getting PR #{pr_number} details for {owner}/{repository}",
            "GET",
            url,
        )

        return {
            "number": pr["number"],
            "created_at": pr.get("created_at"),
            "closed_at": pr.get("closed_at"),
            "merged_at": pr.get("merged_at"),
            "user": pr.get("user", {}).get("login"),
            "additions": pr.get("additions"),
            "deletions": pr.get("deletions"),
            "changed_files": pr.get("changed_files"),
        }

    def get_pull_request_reviews(
        self, owner: str, repository: str, pr_number: int, per_page: int = 100
    ) -> List[dict]:
        """
        Get reviews for a specific pull request with full pagination.

        Args:
            owner: Repository owner
            repository: Repository name
            pr_number: Pull request number
            per_page: Results per page (max 100)

        Returns:
            List of review records with user, state, submitted_at
        """
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        all_reviews: List[dict] = []
        page = 1

        while True:
            logger.info(
                f"Getting reviews for PR #{pr_number} in {owner}/{repository}, page {page}"
            )
            url = (
                f"{API_URL}/repos/{owner}/{repository}/pulls/{pr_number}/reviews"
                f"?per_page={per_page}&page={page}"
            )

            page_reviews = self._execute_api_call(
                f"Getting reviews for PR #{pr_number} in {owner}/{repository}",
                "GET",
                url,
            )

            if not page_reviews:
                break

            for review in page_reviews:
                all_reviews.append({
                    "user": review.get("user", {}).get("login"),
                    "state": review.get("state"),
                    "submitted_at": review.get("submitted_at"),
                })

            if len(page_reviews) < per_page:
                break

            page += 1

        return all_reviews

    def get_merged_prs_with_reviews(
        self, owner: str, repository: str, since_days: int = 30
    ) -> List[dict]:
        """
        Fetch merged PRs and their reviews in a single paginated GraphQL query,
        replacing the N+1 REST call pattern.

        Args:
            owner: Repository owner
            repository: Repository name
            since_days: Used to compute a creation-date cutoff for early
                        pagination exit (since_days * 3). Caller is responsible
                        for filtering results to the desired window.

        Returns:
            List of PR dicts with standard PR fields plus an embedded "reviews"
            list. Each review has "user", "state", and "submitted_at" keys.
        """
        if len(owner.strip()) == 0:
            raise ValueError("owner cannot be blank")
        if len(repository.strip()) == 0:
            raise ValueError("repository cannot be blank")

        page_cutoff_days = since_days * 3
        now_utc = datetime.now(timezone.utc)

        all_prs: List[dict] = []
        cursor: Optional[str] = None

        while True:
            variables: dict = {"owner": owner, "repo": repository, "cursor": cursor}
            body = self._execute_graphql(
                f"PRs with reviews for {owner}/{repository}",
                PULL_REQUESTS_WITH_REVIEWS_TEMPLATE,
                variables,
            )

            pull_requests = body["data"]["repository"]["pullRequests"]
            nodes = pull_requests["nodes"]

            if not nodes:
                break

            for node in nodes:
                review_data = node.get("reviews") or {}
                if review_data.get("pageInfo", {}).get("hasNextPage"):
                    logger.warning(
                        f"PR #{node['number']} has >100 reviews; only first 100 fetched"
                    )
                reviews = [
                    {
                        "user": (r.get("author") or {}).get("login"),
                        "state": r.get("state"),
                        "submitted_at": r.get("submittedAt"),
                    }
                    for r in review_data.get("nodes", [])
                ]
                all_prs.append({
                    "number": node["number"],
                    "created_at": node.get("createdAt"),
                    "closed_at": node.get("closedAt"),
                    "merged_at": node.get("mergedAt"),
                    "user": (node.get("author") or {}).get("login"),
                    "additions": node.get("additions"),
                    "deletions": node.get("deletions"),
                    "changed_files": node.get("changedFiles"),
                    "reviews": reviews,
                })

            page_info = pull_requests["pageInfo"]
            if not page_info["hasNextPage"]:
                break

            # Early exit: stop paginating once the oldest PR on this page was
            # created far enough back that subsequent pages can't be in window
            oldest_created_str = min(
                (n["createdAt"] for n in nodes if n.get("createdAt")),
                default=None,
            )
            if oldest_created_str:
                try:
                    oldest_dt = datetime.fromisoformat(
                        oldest_created_str.replace("Z", "+00:00")
                    )
                    if (now_utc - oldest_dt).days > page_cutoff_days:
                        break
                except (ValueError, AttributeError):
                    pass

            cursor = page_info["endCursor"]

        return all_prs
