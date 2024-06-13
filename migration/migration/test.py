# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import re


def convert_markdown(input: str) -> str:
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


sample = """
h2. whatever

# a
# b [link|https://eheread?sdfasdfasdfa sdfasdfasdf asdf]

h3. another

* c
* d

kkloreklsd faksu;da kdsnfah;ksdhf aksdfkl;adskfja sdkfj a;klsjf aksdjf a
sd aksdf;klas fads [linkk|
https://example.com/asdfasdfasdf+asdfasdfasd+adsf]

{code:java}
something
{code}


{code:sql}
something else
{code}

{quote}
blockquote
{quote}

"""

print(convert_markdown(sample))
