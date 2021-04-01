import json
import logging
import os
import requests
from datetime import date
from requests.auth import HTTPBasicAuth

log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

github_graphql_api = "https://api.github.com/graphql"
github_user = "jmlrt"
# TODO: check why github token can't see activity on private repos
github_token = os.environ["GITHUB_TOKEN"]
# TODO:
# - allow overriding date via command line parameters
# - check only activity from the selected day (current behavior current day until now)
# date = "2021-03-31T00:00:00.000+00:00"
today = f"{date.today()}T00:00:00.000+00:00"

logging.debug(f"GITHUB_TOKEN: {github_token}")

query_head = (
    "query MyQuery {\n"
    f'  user(login: "{github_user}") {{\n'
    f'    contributionsCollection(from: "{today}") {{\n'
)
query_body = """
      pullRequestReviewContributions(first: 100) {
        nodes {
          pullRequest {
            url
            title
          }
        }
      }
      pullRequestContributions(first: 100) {
        nodes {
          pullRequest {
            url
            title
          }
        }
      }
      commitContributionsByRepository {
        contributions(first: 100) {
          totalCount
          nodes {
            repository {
              url
            }
          }
        }
      }
      issueContributions(first: 100) {
        totalCount
        nodes {
          issue {
            title
            url
          }
        }
      }
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

logging.info(today)

query = query_head + query_body
logging.debug(f"QUERY: {query}")

query_json = {"query": query}
response = requests.post(
    github_graphql_api, json=query_json, auth=HTTPBasicAuth(github_user, github_token)
)

data = response.json()["data"]

logging.debug(f"DATA: {json.dumps(data, indent=2)}")

pull_requests = data["user"]["contributionsCollection"]["pullRequestContributions"]
pull_requests_list = [
    f'{r["pullRequest"]["url"]} - {r["pullRequest"]["title"]}'
    for r in pull_requests["nodes"]
]
logging.info(f"Pull Requests: {len(pull_requests_list)}")
for pull_request in pull_requests_list:
    logging.info(pull_request)

commits = data["user"]["contributionsCollection"]["commitContributionsByRepository"]
commits_list = [
    {"count": r["contributions"]["totalCount"], "repos": r["contributions"]["nodes"]}
    for r in commits
]
total_commits = data["user"]["contributionsCollection"]["totalCommitContributions"]
logging.info(f"Commits: {total_commits}")
for commits in commits_list:
    count = commits["count"]
    for repo in commits["repos"]:
        repo_url = repo["repository"]["url"]
        logging.info(f"{repo_url}: {count}")

reviews = data["user"]["contributionsCollection"]["pullRequestReviewContributions"]
reviews_list = [
    f'{r["pullRequest"]["url"]} - {r["pullRequest"]["title"]}' for r in reviews["nodes"]
]
logging.info(f"Reviews: {len(reviews_list)}")
for review in reviews_list:
    logging.info(review)

issues = data["user"]["contributionsCollection"]["issueContributions"]
issues_list = [
    f'{r["pullRequest"]["url"]} - {r["pullRequest"]["title"]}' for r in issues["nodes"]
]
logging.info(f"Issues: {len(issues_list)}")
for issue in issues_list:
    logging.info(issue)
