#!/usr/bin/env python3

import argparse
import json
import subprocess
from collections import Counter

data = []


def get_data(repository):
    response = subprocess.check_output(
        [
            "curl",
            "-s",
            "https://api.github.com/search/issues?q=repo:{}+is:pr+is:open&per_page=100".format(
                repository
            ),
        ]
    )
    raw_data = json.loads(response)

    for d in raw_data["items"][::-1]:
        pull_request = {}
        pull_request["author"] = d["user"]["login"]
        pull_request["url"] = d["pull_request"]["html_url"]
        pull_request["title"] = d["title"]
        data.append(pull_request)
    return data


def top_authors(repository):
    data = get_data(repository)
    authors = [d["author"] for d in data]
    print(Counter(authors).most_common(5))


def list_pull_requests(repository):
    data = get_data(repository)
    sorted_data = sorted(data, key=lambda i: i["author"])
    for d in sorted_data:
        print("{} - {} - {}".format(d["author"], d["url"], d["title"]))


def main():
    parser = argparse.ArgumentParser(description="check GitHub pull requests")
    parser.add_argument("-r", "--repository", required=True, help="A GitHub repository")

    subparsers = parser.add_subparsers()

    parser_top_authors = subparsers.add_parser(
        "top-authors", help="get the top 5 of pull requests authors"
    )
    parser_top_authors.set_defaults(func=top_authors)

    parser_list_pull_requests = subparsers.add_parser(
        "list-pull-requests", help="list pull requests sorted by authors"
    )
    parser_list_pull_requests.set_defaults(func=list_pull_requests)

    args = parser.parse_args()

    # Print help if there is no positionnal argument
    try:
        args.func(args.repository)
    except AttributeError:
        parser.print_help()


if __name__ == "__main__":
    main()
