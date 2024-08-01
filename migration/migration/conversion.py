# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import re


def convert_markdown(input: str) -> str:
    if input is None or input == "":
        return ""

    output = re.sub(r"\n\s*#", "\n1.", input)
    output = re.sub("h1.", "#", output)
    output = re.sub("h2.", "##", output)
    output = re.sub("h3.", "###", output)
    output = re.sub("h4.", "####", output)

    output = re.sub(r"{code:([^}]+)}", r"\n```\1\n", output)
    output = re.sub("{code}", "\n```\n", output)

    # convert links
    output = re.sub(r"\[([^|]+)\|([^\]]+)\]", r"[\1](\2)", output)

    # This doesn't get new lines right. Just ignore and let it go.
    # output = re.sub("{quote}\n", r"> ", output)

    return output


# sample = """
# h4. Items
# # Create a shell React App under src/web folder
#  # Add styles based on the UI assets from Jonathan and create a layout structure.

# h4. Acceptance: 

# Web app loads and layout matches the UX.

# """

# print(convert_markdown(sample))
