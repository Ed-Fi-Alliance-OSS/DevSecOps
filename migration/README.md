# Jira to GitHub Issue Migrator

Simple script for reading issues from Jira and pushing them to GitHub Issues.

> [!NOTE]
> This is a "quick and dirty" script with no test automation. Not intended
> to be a robust enterprise tool.

## Running the Script

1. Initialize virtual environment and install dependencies:

   ```shell
   poetry install
   ```

2. Setup the following variables, either in the environment or in a `.env` file:

    ```env
    # Access token from Jira
    JIRA_TOKEN

    # Example: https://tracker.ed-fi.org
    JIRA_BASE_URL

    # Example: ODS
    JIRA_PROJECT_KEY

    # INFO and DEBUG provide additional details. Any other setting is
    # treated as ERROR only. Default: INFO
    LOG_LEVEL

    # Default: 100
    PAGE_SIZE

    # A GitHub access token with permission to write to Issues in the given repository.
    GITHUB_TOKEN

    # Full organization/repository name
    GITHUB_REPOSITORY
    ```

3. Run the script:

   ```shell
   poetry run python migration
   ```

## References

* [PyGitHub](https://pygithub.readthedocs.io/)
* [Python Jira](https://jira.readthedocs.io/)

## Legal Information

Copyright (c) 2024 Ed-Fi Alliance, LLC and contributors.

Licensed under the [Apache License, Version 2.0](../LICENSE) (the "License").

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
