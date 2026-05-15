# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_tech_metrics.settings import Configuration, load_configuration


def test_info_prints_at_info_level(capsys):
    conf = Configuration("u", "t", "http://x", "INFO", 100)
    conf.info("hello-info")
    captured = capsys.readouterr()
    assert "hello-info" in captured.out


def test_info_prints_at_debug_level(capsys):
    conf = Configuration("u", "t", "http://x", "DEBUG", 100)
    conf.info("hello-debug")
    captured = capsys.readouterr()
    assert "hello-debug" in captured.out


def test_info_suppressed_at_error_level(capsys):
    conf = Configuration("u", "t", "http://x", "ERROR", 100)
    conf.info("hello-suppressed")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_debug_prints_at_debug_level(capsys):
    conf = Configuration("u", "t", "http://x", "DEBUG", 100)
    conf.debug("dbg-msg")
    captured = capsys.readouterr()
    assert "dbg-msg" in captured.out


def test_debug_suppressed_at_info_level(capsys):
    conf = Configuration("u", "t", "http://x", "INFO", 100)
    conf.debug("dbg-suppressed")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_error_always_prints(capsys):
    conf = Configuration("u", "t", "http://x", "ERROR", 100)
    conf.error("err-msg")
    captured = capsys.readouterr()
    assert "err-msg" in captured.out


def test_load_configuration_returns_correct_fields():
    args = ["-u", "testuser", "-t", "testtoken", "-b", "http://jira.example.com"]
    conf = load_configuration(args)
    assert conf.jira_user_name == "testuser"
    assert conf.jira_token == "testtoken"
    assert conf.jira_base_url == "http://jira.example.com"
    assert conf.log_level == "INFO"
    assert conf.page_size == 100


def test_load_configuration_invalid_log_level_raises_system_exit():
    with pytest.raises(SystemExit):
        load_configuration(
            ["-u", "user", "-t", "tok", "-b", "http://x", "-l", "INVALID"]
        )
