# Ed-Fi Repo Auditor

Python script to report on compliance with Ed-Fi repository guidance. The file
[scoring.json](./scoring.json) provides the guidelines to be followed; see below
for a detailed description in plain text. The property names are in the same
format that the code will follow to assign a value. This file provides a value
for each property, this file can be modified accordingly. Additionally, the
`threshold` property specifies the limit that will be tolerated to indicate if
the repository needs to make adjustments according to the scoring.

## Run from GitHub Actions

Find the "Run Single Audit" workflow in the Actions tab, and click "Run workflow". Unless testing code updates in a branch, leave the branch selection as "main". Then, provide the required parameters and click "Run workflow". Look for the workflow run in the list of runs, and click into it. Click on the "Run Ed-Fi Repo Auditor" step to see the console output from the script, including the scoring results.

Required parameters:

- Organization: choose from `Ed-Fi-Alliance-OSS`, `Ed-Fi-Closed`, and `Ed-Fi-Exchange-OSS`.
- Repository name: :exclamation: this is case sensitive; if you get the wrong case, the OSSF score will not be included in the results. You can find the correct case by going to the repository on GitHub and looking at the URL.

## Run Locally

To run, install [poetry](https://python-poetry.org/) and run:

```bash
poetry run python edfi_repo_auditor -p {TOKEN} -s True -o {ORGANIZATION} -r {REPOSITORY}
```

Parameters:

| Parameter          | Description          | Required?                                                                             |
| ------------------ | -------------------- | ------------------------------------------------------------------------------------- |
| --access_token  -p | GitHub Access Token  | To call private repos and get branch protection info                                  |
| --organization -o  | Organization Name    | Yes                                                                                   |
| --repositories -r  | Repositories         | No. If not specified, will get all repos for the organization.                        |
| --log_level -l     | Log level            | No. Default: INFO. Can be: ERROR, WARNING, INFO, DEBUG                                |
| --save_results -s  | Save results to file | No. Default: console. If specified, will save the  results to a file                  |
| --file_name -f     | Filename             | No. Default: `audit-results`. If specified, will save the results with given name.    |
| --no_verify_ssl    | Do not verify certs  | No. Default: False. If specified, will not verify SSL certificates (not recommended). |

Alternatively, you can copy `.env.example` to `.env`, add your GitHub API token,
and skip all of the arguments: `poetry run python edfi_repo_auditor`.

Look in the `reports` directory for the output file and an HTML file summarizing
the scoring results.

## Dev Tools

| Command              | Purpose     |
| -------------------- | ----------- |
| `poetry run pytest`  | unit tests  |
| `poetry run mypy .`  | type checks |
| `poetry run black .` | re-format   |
| `poetry run flake8`  | linter      |

## Detailed Guidance

### Standard files

- **Has SECURITY**: There is a SECURITY.md file.
- **Has CONTRIBUTORS.md**: There is a CONTRIBUTORS.md file.
- **Has NOTICES**: There is a NOTICES.md file.
- **Has LICENSE**: There is either a LICENSE file.
- **Has AGENTS.md**: There is an AGENTS.md file.

### Standard Actions Usage

- **Has Actions**: There is at least one Action in the repository.
- **Uses CodeQL**: The repository runs CodeQL; detected by looking for "uses: github/codeql-action/analyze" in an Actions yml file.
- **Uses only approved GitHub Actions**: The repository only uses approved GitHub Actions; detected by looking for "repository-scanner.yml" in an Actions yml file.
- **Uses Test Reporter**: Unit tests results are uploaded directly into GitHub Actions; detected by looking for "uses: dorny/test-reporter" in an Actions yml file.
- **Has Unit Tests**: There is at least one unit test; detected by looking for "test" in the name of an Actions yml file.

### Branch Rules

- **Requires PR**: Branch protection for `main` requires a pull request, which also implies requiring a code review.
- **Admin cannot bypass PR**: Branch protection for `main` cannot be bypassed by an admin.
- **Restricts creation**: Branch protection for `main` restricts who can create branches.
- **Restricts deletion**: Branch protection for `main` restricts who can delete branches
- **Requires linear history**: Branch protection for `main` requires a linear history, which implies no merge commits.
- **Admin cannot bypass PR**: Branch protection for `main` does not allow admins to push directly to the branch.

### Repository Features

- **Wiki Disabled**: Wikis are disabled.
- **Issues Enabled**: Issues are enabled.
- **Projects Disabled**: Projects are disabled.
- **Deletes head branch**: Automatically deletes head branches on merge.
- **Uses Squash Merge**: Squash merge is the default.
- **License Information**: The repo settings specify a license (this is different than the license file).

### Security

- **Dependabot Enabled**: Dependabot is enabled.
- **Dependabot Alerts**: There are no _critical_ or _high_ severity DependaBot alerts that have remained open for greater than three weeks.
- **OSSF Score**: the repository score calculated by the OSSF Scorecard.

### Pull Request Metrics

- **Number of Merged PRs (last 30 days)**: The total number of pull requests merged in the last 30 days, just informational.
- **Avg Reviews per PR**: The average number of reviews received per pull request, just informational.
- **Avg Approvals per PR**: The average number of approvals received per pull request, just informational.
- **Avg Lead Time (days)**: The average lead time in days (time from PR creation to merge). Monitoring for trends, no baseline requirement _yet_.
- **Avg PR Duration (days)**: The average PR duration in days (time from PR creation to close). Monitoring for trends, no baseline requirement _yet_.
- **Avg Time to First Approval (hours)**: The average time to first approval in hours. Monitoring for trends, no baseline requirement _yet_.
- **Top 3 Reviewers**: The three most frequent reviewers by number of reviews. Just informational.
- **Top Reviewer Share (%)**: The percentage of reviews performed by the top reviewer. Monitor to make sure the burden is not falling primarily on one person.
- **Total Reviewers**: The total number of reviewers who have participated in the repository. Just informational.
- **Unique Reviewers**: The total number of unique reviewers who have participated in the repository. Just informational.
