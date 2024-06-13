# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from typing import List, Tuple, Optional
import re

from jira import JIRA, Issue
from jira.client import ResultList

from settings import Configuration

# This value varies from one installation to the next. The following constant was discovered
# by inspecting the output from `GET https://tracker.ed-fi.org/rest/agile/1.0/board/167/backlog`
STORY_POINTS_FIELD = "customfield_10004"


def convert_markdown(input: str) -> str:
    # sometimes a non-string seems to come through
    output = str(input)

    output = re.sub(r"\n#", "\n1.", input)
    output = re.sub("h1.", "#", output)
    output = re.sub("h2.", "##", output)
    output = re.sub("h3.", "###", output)
    output = re.sub("h4.", "####", output)

    output = re.sub(r"{code:([^}]+)}", r"\n```\1\n", output)
    output = re.sub("{code}", "\n```\n", output)

    # convert links
    output = re.sub(r"\[([^|]+)\|([^\]]+)\]", r"[\1](\2)", output)

    return output


@dataclass
class EdFiComment:
    author: str
    created: str
    body: str

    def create_gh_comment(self) -> str:
        return f"""# Jira Comment

{convert_markdown(self.body)}

# Jira Metadata
Created: {self.created}
Commenter: {self.author}
"""


@dataclass
class EdFiIssue:
    project_key: str
    issue_key: str
    created: str
    story_points: str
    fixVersion: str
    issueType: str
    status: str
    labels: List[str]
    priority: str
    description: str
    comments: List[EdFiComment]
    reporter: str
    title: str
    epic: str

    def create_gh_description(self) -> str:
        return f"""# Jira Description

{convert_markdown(self.description)}

# Jira Metadata
Key: {self.issue_key}
Epic: {self.epic}
Created: {self.created}
Reporter: {self.reporter}
"""

    def get_gh_labels(self) -> str:
        self.story_points = self.story_points or "0"
        return [
            self.issueType,
            self.status,
            f"points: {self.story_points}",
            *self.labels,
        ]


@dataclass
class IssuePage:
    issue_list: List[EdFiIssue]
    last_key: Optional[str]


class JiraBrowser:

    def __init__(self, conf: Configuration):
        self.conf = conf

        conf.info(f"Connecting to {conf.jira_base_url}")
        self.jira = JIRA(conf.jira_base_url, token_auth=conf.jira_token)

    def get_page_of_issues(self, project_key: str, begin: str) -> IssuePage:
        jql = f"project={project_key} {begin} order by created asc"

        self.conf.debug(jql)
        fields = f"{STORY_POINTS_FIELD},key,created,fixVersions,issuetype,labels,priority,fixVersions,status,description,comment,reporter,summary,epic"
        issues: ResultList[Issue] = self.jira.search_issues(jql, maxResults=self.conf.page_size, fields=fields)  # type: ignore  # have never seen it return the alternate dictionary

        last: str = ""
        if len(issues) == self.conf.page_size:
            last = f"AND key >= {str(issues[-1].key)}"

        return IssuePage(
            [
                EdFiIssue(
                    project_key,
                    i.key,
                    i.fields.created,
                    i.fields.customfield_10004,
                    (
                        i.fields.fixVersions[0].name
                        if len(i.fields.fixVersions) > 0
                        else ""
                    ),
                    i.fields.issuetype.name,
                    i.fields.status.name,
                    i.fields.labels,
                    i.fields.priority.name,
                    i.fields.description,
                    [
                        EdFiComment(c.author.displayName, c.created, c.body)
                        for c in i.fields.comment.comments
                    ],
                    i.fields.reporter.displayName,
                    i.fields.summary,
                    (
                        i.raw["fields"]["epic"]["key"]
                        + ", "
                        + i.raw["fields"]["epic"]["name"]
                        if "epic" in i.raw["fields"]
                        else "n/a"
                    ),
                )
                for i in issues
            ],
            last,
        )

    def get_project(self, project: str) -> List[Tuple[str, ...]]:
        data = []

        begin = ""

        # "Do...While" type loop to get all pages of data.
        while True:
            page = self.get_page_of_issues(project, begin)

            data.extend(page.issue_list)

            if page.last_key == "":
                break

            # Next request to get_issues needs to look for items _after_ the last one received
            begin = page.last_key or ""

        return data
