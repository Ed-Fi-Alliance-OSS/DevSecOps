# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from typing import Optional, List

from dotenv import load_dotenv
from configargparse import ArgParser


@dataclass
class Configuration:
    """
    Container for holding arguments parsed from command line or environment.
    """

    organization: str
    personal_access_token: str
    repository: Optional[str]


def load_configuration(args_in: List[str]) -> Configuration:

    load_dotenv()

    parser = ArgParser()
    parser.add(  # type: ignore
        "-o",
        "--organization",
        required=True,
        help="GitHub organization name",
        type=str,
        env_var="AUDIT_ORGANIZATION"
    )

    parser.add(  # type: ignore
        "-p",
        "--access_token",
        required=True,
        help="GitHub personal access token (PAT) with repo read permission",
        type=str,
        env_var="AUDIT_ACCESS_TOKEN"
    )

    parser.add(  # type: ignore
        "-r",
        "--repository",
        required=False,
        help="Specific repository to audit",
        type=str,
        env_var="AUDIT_REPOSITORY"
    )

    parsed = parser.parse_args(args_in)

    return Configuration (
        parsed.organization,
        parsed.access_token,
        parsed.repository
    )
