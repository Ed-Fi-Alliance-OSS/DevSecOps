# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_repo_auditor.config import Configuration, load_configuration

ORGANIZATION_1 = "Ed-Fi-Alliance-OSS"
REPOSITORY_1 = "Analytics-Middle-Tier"
PERSONAL_ACCESS_TOKEN_1 = "asdfasdfasdfasdfasdfas"

ORGANIZATION_2 = "__Ed-Fi-Alliance-OSS"
REPOSITORY_2 = "__Analytics-Middle-Tier"
PERSONAL_ACCESS_TOKEN_2 = "__asdfasdfasdfasdfasdfas"


def assert_no_error_reported(capsys):
    out, err = capsys.readouterr()

    assert err == "", "Error output has a message"
    assert out == "", "Standard output has a message"


def describe_when_loading_configuration() -> None:
    @pytest.fixture
    def clear_env(monkeypatch) -> None:
        monkeypatch.delenv("AUDIT_ORGANIZATION", raising=False)
        monkeypatch.delenv("AUDIT_ACCESS_TOKEN", raising=False)
        monkeypatch.delenv("AUDIT_REPOSITORY", raising=False)

        return monkeypatch

    def describe_given_no_parameters_provided() -> None:
        def it_should_print_a_message_to_the_console(clear_env, capsys) -> None:
            with pytest.raises(SystemExit):
                _ = load_configuration([])

                _, err = capsys.readouterr()

                assert err != ""

    def describe_given_all_parameters_via_cli() -> None:
        @pytest.fixture
        def result() -> Configuration:
            args_in = [
                "-o",
                ORGANIZATION_1,
                "-p",
                PERSONAL_ACCESS_TOKEN_1,
                "-r",
                REPOSITORY_1
            ]

            return load_configuration(args_in)

        def config_should_include_the_organization(clear_env, result: Configuration) -> None:
            assert result.organization == ORGANIZATION_1

        def config_should_include_the_access_token(clear_env, result: Configuration) -> None:
            assert result.personal_access_token == PERSONAL_ACCESS_TOKEN_1

        def config_should_include_the_repository(clear_env, result: Configuration) -> None:
            assert result.repository == REPOSITORY_1

        def it_should_not_report_any_errors(clear_env, capsys, result: Configuration) -> None:
            assert_no_error_reported(capsys)

    def describe_given_only_required_parameters_via_cli() -> None:
        @pytest.fixture
        def result() -> Configuration:
            args_in = [
                "-o",
                ORGANIZATION_1,
                "-p",
                PERSONAL_ACCESS_TOKEN_1
            ]

            return load_configuration(args_in)

        def config_should_include_the_organization(clear_env, result: Configuration) -> None:
            assert result.organization == ORGANIZATION_1

        def config_should_include_the_access_token(clear_env, result: Configuration) -> None:
            assert result.personal_access_token == PERSONAL_ACCESS_TOKEN_1

        def config_should_not_include_a_repository(clear_env, result: Configuration) -> None:
            assert result.repository is None

        def it_should_not_report_any_errors(clear_env, capsys, result: Configuration) -> None:
            assert_no_error_reported(capsys)


    def describe_given_all_parameters_via_env() -> None:
        @pytest.fixture
        def result(monkeypatch) -> Configuration:
            monkeypatch.setenv("AUDIT_ORGANIZATION", ORGANIZATION_1)
            monkeypatch.setenv("AUDIT_ACCESS_TOKEN", PERSONAL_ACCESS_TOKEN_1)
            monkeypatch.setenv("AUDIT_REPOSITORY", REPOSITORY_1)

            return load_configuration([])

        def config_should_include_the_organization(clear_env, result: Configuration) -> None:
            assert result.organization == ORGANIZATION_1

        def config_should_include_the_access_token(clear_env, result: Configuration) -> None:
            assert result.personal_access_token == PERSONAL_ACCESS_TOKEN_1

        def config_should_include_the_repository(clear_env, result: Configuration) -> None:
            assert result.repository == REPOSITORY_1

        def it_should_not_report_any_errors(clear_env, capsys, result: Configuration) -> None:
            assert_no_error_reported(capsys)


    def describe_given_only_required_parameters_via_env() -> None:
        @pytest.fixture
        def result(monkeypatch) -> Configuration:
            monkeypatch.setenv("AUDIT_ORGANIZATION", ORGANIZATION_1)
            monkeypatch.setenv("AUDIT_ACCESS_TOKEN", PERSONAL_ACCESS_TOKEN_1)

            return load_configuration([])

        def config_should_include_the_organization(clear_env, result: Configuration) -> None:
            assert result.organization == ORGANIZATION_1

        def config_should_include_the_access_token(clear_env, result: Configuration) -> None:
            assert result.personal_access_token == PERSONAL_ACCESS_TOKEN_1

        def config_should_not_include_a_repository(clear_env, result: Configuration) -> None:
            assert result.repository is None

        def it_should_not_report_any_errors(clear_env, capsys, result: Configuration) -> None:
            assert_no_error_reported(capsys)

    def describe_given_all_parameters_via_both_cli_and_env() -> None:
        @pytest.fixture
        def result(monkeypatch) -> Configuration:
            monkeypatch.setenv("AUDIT_ORGANIZATION", ORGANIZATION_2)
            monkeypatch.setenv("AUDIT_ACCESS_TOKEN", PERSONAL_ACCESS_TOKEN_2)
            monkeypatch.setenv("AUDIT_REPOSITORY", REPOSITORY_2)

            args_in = [
                "-o",
                ORGANIZATION_1,
                "-p",
                PERSONAL_ACCESS_TOKEN_1,
                "-r",
                REPOSITORY_1
            ]

            return load_configuration(args_in)

        def config_should_include_the_organization_from_cli(clear_env, result: Configuration) -> None:
            assert result.organization == ORGANIZATION_1

        def config_should_include_the_access_token_from_cli(clear_env, result: Configuration) -> None:
            assert result.personal_access_token == PERSONAL_ACCESS_TOKEN_1

        def config_should_include_the_repository_from_cli(clear_env, result: Configuration) -> None:
            assert result.repository == REPOSITORY_1

        def it_should_not_report_any_errors(clear_env, capsys, result: Configuration) -> None:
            assert_no_error_reported(capsys)
