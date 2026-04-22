# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# Original context-manager technique courtesy of Stack Overflow user "Blender"
# https://stackoverflow.com/a/15445989/30384

import contextlib
from collections.abc import Generator, MutableMapping
from typing import Any, Optional
import warnings

import requests
from urllib3.exceptions import InsecureRequestWarning

_old_merge_environment_settings = requests.Session.merge_environment_settings


@contextlib.contextmanager
def no_ssl_verification() -> Generator[None, None, None]:
    """
    Context manager that disables SSL certificate verification for all
    requests made via the ``requests`` library within the block.

    Warnings about unverified HTTPS connections are suppressed as well.
    Any adapters opened during the block are closed on exit so that the
    ``verify=False`` override does not leak across connection keep-alive.
    """
    opened_adapters: set = set()

    def merge_environment_settings(  # type: ignore[override]
        self: requests.Session,
        url: str | bytes | None,
        proxies: Optional[MutableMapping[str, str]],
        stream: Optional[bool],
        verify: Optional[bool | str],
        cert: Optional[str | tuple[str, str]],
    ) -> Any:
        opened_adapters.add(self.get_adapter(url))  # type: ignore[arg-type]
        settings = _old_merge_environment_settings(
            self, url, proxies, stream, verify, cert
        )
        settings["verify"] = False
        return settings

    requests.Session.merge_environment_settings = merge_environment_settings  # type: ignore[method-assign, assignment]

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = _old_merge_environment_settings  # type: ignore[method-assign]

        for adapter in opened_adapters:
            try:
                adapter.close()
            except Exception:
                pass
