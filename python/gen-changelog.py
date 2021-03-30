#!/usr/bin/env python3

import json
import subprocess
import sys

if len(sys.argv) == 2:
    repo = sys.argv[1]
else:
    print(f"Usage: {sys.argv[0]} <github_org>/<github_repo> (example: jmlrt/toolbox)")
    sys.exit(1)

response = subprocess.check_output(
    [
        "curl",
        "-s",
        f"https://api.github.com/search/issues?q=repo:{repo}+is:pr+is:merged+sort:updated&per_page=1000",
    ]
)

print(
    "| PR                                                      | Author                                                     | Title                                                     |\n| ------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------- |"
)
data = json.loads(response)
for d in data["items"][::-1]:
    url = d["pull_request"]["html_url"]
    number = d["number"]
    title = d["title"]
    user = d["user"]["login"]
    avatar = d["user"]["avatar_url"] + "&s=30"
    user_url = d["user"]["html_url"]
    print(f"|[#{number}]({url}) | [@{user}]({user_url}) | {title}|")
