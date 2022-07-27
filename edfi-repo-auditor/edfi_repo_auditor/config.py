# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from typing import List

from configargparse import ArgParser


DEFAULT_LOG_LEVEL = "INFO"


@dataclass
class Configuration:
    """
    Container for holding arguments parsed from command line or environment.
    """

    organization: str
    personal_access_token: str
    repositories: List[str]
    log_level: str
    save_results: bool


def load_configuration(args_in: List[str]) -> Configuration:

    parser = ArgParser()
    parser.add(  # type: ignore
        "-o",
        "--organization",
        required=True,
        help="GitHub organization name",
        type=str,
        env_var="AUDIT_ORGANIZATION",
    )

    parser.add(  # type: ignore
        "-p",
        "--access_token",
        required=True,
        help="GitHub personal access token (PAT) with repo read permission",
        type=str,
        env_var="AUDIT_ACCESS_TOKEN",
    )

    parser.add(  # type: ignore
        "-r",
        "--repositories",
        required=False,
        help="Specific repositories to audit",
        default=[],
        type=str,
        nargs="+",
        env_var="AUDIT_REPOSITORIES",
    )

    parser.add(  # type: ignore
        "-l",
        "--log_level",
        required=False,
        help="Log level (default: info)",
        default=DEFAULT_LOG_LEVEL,
        type=str,
        env_var="AUDIT_LOG_LEVEL",
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
    )

    parser.add(  # type: ignore
        "-s",
        "--save_results",
        required=False,
        help="Save results into file",
        default=False,
        type=bool,
        env_var="AUDIT_FILE_PATH",
    )

    parsed = parser.parse_args(args_in)

    return Configuration(
        parsed.organization, parsed.access_token, parsed.repositories, parsed.log_level, parsed.save_results
    )
