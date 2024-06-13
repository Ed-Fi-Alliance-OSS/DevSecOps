# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
import logging
import sys
from os import getenv

from termcolor import colored

from dotenv import load_dotenv

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_PAGE_SIZE = 100


@dataclass
class Configuration:
    """
    Container for holding arguments parsed from command line or environment.
    """

    jira_token: str
    jira_base_url: str
    log_level: str
    page_size: int
    github_token: str

    def info(self, message: str) -> None:
        if self.log_level in ("INFO", "DEBUG"):
            print(colored(message, "blue"))

    def debug(self, message: str) -> None:
        if self.log_level in ("DEBUG"):
            print(colored(message, "yellow"))

    def error(self, message: str) -> None:
        print(colored(message, "red"))

    def configure_logging(self) -> None:
        logging.basicConfig(
            stream=sys.stdout,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            level=self.log_level,
        )


def load_from_env() -> Configuration:
    load_dotenv()

    c = Configuration(
        getenv("JIRA_TOKEN", ""),
        getenv("JIRA_BASE_URL", ""),
        getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL),
        int(getenv("PAGE_SIZE", DEFAULT_PAGE_SIZE)),
        getenv("GITHUB_TOKEN", "")
    )
    c.configure_logging()

    return c
