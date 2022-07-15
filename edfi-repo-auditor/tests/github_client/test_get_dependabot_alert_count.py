# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from http import HTTPStatus
from typing import List
import pytest
import requests_mock

from edfi_repo_auditor.github_client import GitHubClient, GRAPHQL_ENDPOINT

ACCESS_TOKEN = "asd09uasdfu09asdfj;iolkasdfklj"


def describe_when_getting_count_of_dependabot_alerts() -> None:
    def describe_given_blank_owner() -> None:
        def it_raises_an_a_ValueError() -> None:
            with pytest.raises(ValueError):
                GitHubClient(ACCESS_TOKEN).get_repositories("")

    def describe_given_valid_owner() -> None:
        def describe_given_valid_query() -> None:
            def describe_there_are_some_alerts() -> None:
                RESULT = """
{
    "data": {
        "repository": {
            "vulnerabilityAlerts": {
                "nodes": [
                    {
                        "createdAt": "2021-07-14T20:19:37Z",
                        "dismissedAt": null,
                        "securityVulnerability": {
                            "package": {
                                "name": "RestSharp"
                            },
                            "advisory": {
                                "description": "RestSharp...",
                                "severity": "HIGH"
                            }
                        }
                    },
                    {
                        "createdAt": "2022-06-22T21:27:04Z",
                        "dismissedAt": null,
                        "securityVulnerability": {
                            "package": {
                                "name": "Newtonsoft.Json"
                            },
                            "advisory": {
                                "description": "Newtonsoft.Json....",
                                "severity": "HIGH"
                            }
                        }
                    }
                ]
            }
        }
    }
}
""".strip()

                @pytest.fixture
                def results() -> int:
                    # Arrange
                    with requests_mock.Mocker() as m:
                        m.post(GRAPHQL_ENDPOINT, status_code=HTTPStatus.OK, text=RESULT)
                        return GitHubClient(ACCESS_TOKEN).get_dependabot_alert_count(
                            "Ed-Fi-Alliance-OSS", "Ed-Fi-ODS"
                        )

                def it_returns_count_of_2(results: List[str]) -> None:
                    assert results == 2

            def describe_there_are_no_alerts() -> None:
                RESULT = """
{
    "data": {
        "repository": {
            "vulnerabilityAlerts": {
                "nodes": []
            }
        }
    }
}
""".strip()

                @pytest.fixture
                def results() -> int:
                    # Arrange
                    with requests_mock.Mocker() as m:
                        m.post(GRAPHQL_ENDPOINT, status_code=HTTPStatus.OK, text=RESULT)
                        return GitHubClient(ACCESS_TOKEN).get_dependabot_alert_count(
                            "Ed-Fi-Alliance-OSS", "Ed-Fi-ODS"
                        )

                def it_returns_count_of_2(results: List[str]) -> None:
                    assert results == 0

        def describe_given_bad_query() -> None:
            RESULT = """
{
  "data": {
    "organization": null
  },
  "errors": [
    {
      "type": "NOT_FOUND",
      "path": [
        "organization"
      ],
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "message": "Could not resolve to an Organization with the login of 'Ed-Fi-Alliance-OSSe'."
    }
  ]
}
""".strip()

            def it_raises_a_RuntimeError() -> None:
                # Arrange
                with requests_mock.Mocker() as m:
                    m.post(GRAPHQL_ENDPOINT, status_code=HTTPStatus.OK, text=RESULT)

                    with pytest.raises(RuntimeError):
                        GitHubClient(ACCESS_TOKEN).get_dependabot_alert_count(
                            "Ed-Fi-Alliance-OSS", "Ed-Fi-ODS"
                        )
