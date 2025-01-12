# code-reviewer
This project allows developers to automatically review pull requests in Azure DevOps using mostly regular expression based checks and actions that can be easily customized in a YAML configuration file.

The script can be configured to run in a loop and wait a certain amount of time between each run.

## Examples:
* Block code that matches patterns that are hard to check with static analysis tools and comment directly on matching lines.
* Reactivate a comment thread if the code matches a pattern.
* Require a reviewer based on the title of a pull request.
* Ensure that the title of a pull request matches a pattern such as starting with `[tags]`.
* Enforce that the description of a pull request matches a pattern.
* Reject a pull request if it has merge conflicts.
* Reject a pull request if the build failed.
* Requeue a build.

## Checks
Each rule can have regular expressions for:
* author
* title
* description
* merge status (to check if there are merge conflicts)
* policy checks (check the build status using JSON Paths)
* file
* line
* source branch
* target branch

See the documentation and examples below for more details.

## Actions
If all of the checks in a rule match, then the actions associated with the rule will run.
Supported actions:
* comment (on the PR overview or a line)
* add tags
* update the title
* requeue a build for a pipeline
* require a reviewer
* vote

See the documentation and examples below for more details.

# Setup
Written using Python 3.10

```bash
pip install --requirement requirements.txt
```

Get a PAT: https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows#create-a-pat

Give the PAT the following permissions:

Scopes:
* Code: Full, Status
* Project and Team: Read
* User Profile: Read
* Pull Request Threads: Read

## Configuration File
Rules are configured in a YAML file.

Example (fill in the values in `{...}` with your own values):
```yaml
organization_url: 'https://dev.azure.com/{organization}'
project: {project_name}
repository_name: {repository_name}

# The number of pull requests to check in each run.
top: 100

# The source branch of the pull requests to check.
# By default, pull requests from all branches are checked.
# pr_branch: 'my-branch'

# The target branch of the pull requests to check.
# By default, pull requests to all branches are checked.
target_branch: 'main'

# The status of the pull requests to check.
# Defaults to 'active'.
# status can be 'abandoned', 'active', 'all', 'completed', 'notSet'
# See https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests/get-pull-requests?view=azure-devops-rest-7.1&tabs=HTTP#pullrequeststatus for more information.
# Note that the script will not comment on pull requests that are completed because the diff cannot be computed if the source branch has been deleted, which most teams do when a pull request is completed.
status: 'active'

# Eventually the script will try to figure out your email and ID automatically.
# Your email associated with ADO.
# This is used to see if you already voted on a pull request.
current_user: {your email}
# To get your ID,
# Go to your profile (e.g, https://dev.azure.com/{organization}/_usersSettings/about).
# Click on your picture to edit it.
# Right click on the picture in the pop-up modal and "Copy image link".
# The link should have "?id={your ID}" in it.
user_id: {your ID}

# Stats
# If enabled, the script can gather commenters statistics.
# is_stats_enabled: true

log_level: INFO

# The amount of seconds to wait after a run of reviewing pull requests.
# If this is not set, then the script will not loop.
wait_after_review_s: 666

# Dry run:
# If true, then the script will not take actions and will just log what it would do at the INFO level.
# Defaults to false.
# is_dry_run: true

# All checks within each rule must match for the rule to be applied.

# Rules can have:
# Checks:
# * author_pattern: A regex pattern that the author's display name or unique name (email) must match.

# * title_pattern: A regex pattern that the title must match.
# * description_pattern: A regex pattern that the description must match.

# * merge_status_pattern: A regex pattern that the merge status must match. Some typical values are: 'conflicts', 'failure', 'queued', 'succeeded'. See https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests/get-pull-requests?view=azure-devops-rest-7.0&tabs=HTTP#pullrequestasyncstatus for more information.

# * is_draft: By default, all pull requests are reviewed. If this is set to true, then only draft pull requests will match the rule. If this is set to false, then only published pull requests will match the rule.

# Branch Patterns
# * source_ref_name_pattern: A regex pattern that the source branch must match. Source branches usually start with 'refs/heads/'.
# * target_ref_name_pattern: A regex pattern that the source branch must match. E.g., 'refs/heads/main'.

# * policy_checks: A list of checks to run for the output of policy evaluations (build checks).
# Every check in the `evaluation_checks` list must match the same policy evaluation for the entire rule to match.
# Note that there can be multiple `evaluation_checks` lists in a rule so that a combination ('AND') of checks can be used to only perform actions based on the output of multiple policy evaluations.
# See https://learn.microsoft.com/en-us/rest/api/azure/devops/policy/evaluations/list for the API output to understand what JSON Paths are possible.
# The examples below show how to use the JSON Paths to check the build status.

# Checking files:
# * file_pattern: A regex pattern that a file path must match. A `diff_pattern` is not required when this is set.
# * diff_pattern: A regex pattern that a new or the new version of a modified line must match in files matching `file_pattern`.

# If all of the checks in a rule match, then any actions specified will be applied.
# Actions:

# * add_tags (list of strings): Tags (AKA labels) to add to the pull request.

# * comment (string): A comment to post on the PR or a line in a diff depending on how the rule matches.
# If the comment already exists, then the comment will not be added again.
# If the thread with the comment is inactive, then the thread will be reactivated.
# If `diff_pattern` is set, then the comment will be on lines that match `diff_pattern`.
# A `comment_id` (string) property is recommended if you want to change the text of the comment instead of adding a new comment in the future.
# If `comment_id` is set, then this ID will be used to identify the comment.
# If there is already a comment with this ID from the user, then instead of adding a new comment,
# the comment with this ID from the current user will be updated (if necessary)
# and the thread will be reactivated (if necessary).
# The `comment_id` is appended as a HTML comment.
# To add a `comment_id` to an existing rule, first, do not change the `comment`.
# Add just the `comment_id` and then run the script.
# The script will add the `comment_id` to existing comments since the `comment` is the same.
# Now you can change the `comment` so that the comment will be updated when the script runs again.

# * new_title (string): A new title to set on the pull request. Use "{TITLE}" as a placeholder for the current title.

# * requeue (list of checks): A list of checks to run for the output of policy evaluations (build checks). The policy where all checks match will be requeued.

# * requeue_comment (string): A comment to post on the PR when requeuing a build.

# * require (string): The ID of someone to require.

# * vote (int): The vote to give if the rule matches.

# Requeuing
# Use a list of checks to specify the policy evaluation (build check) to requeue.
# See the example below for more details.

# Voting
# Use a number or a string (case is ignored) if you want to vote when the checks match.
# The script will only vote if the new vote would be more rejective than your current vote
# or if your current vote is not set and the new vote is to approve or approve with suggestions.
# This is to avoid approving if you have already voted.
# Below are the string values (in quotes) and numbers (based on the ADO API) accepted for the `vote` action:
# * Approve ("approve"): 10
# * Approve with suggestions ("approve_with_suggestions"): 5
# * No vote or reset: ("none" or "reset"): 0
# * Waiting for author ("wait"): -5
# * Reject ("REJECT"): -10

# Examples:
rules:
  # If the title does not start with a tag, then vote to reject.
  - title_pattern: '^(?!\[[^]]{2,}\])'
    comment: "Please add at least one tag in square brackets at the beginning of the pull request title with nothing before the tag, not even whitespace."
    comment_id: "title_tag"
    vote: REJECT

  # A simple check for titles that do not use the imperative mood.
  - title_pattern: '(?i)^.*(?:\[[^]]*]\s*)*(?:Add|Correct|Updat)(?:ed|ing)\b'
    comment: "Automated comment: Please use the imperative mood (\"Add\" instead of \"Adding\" or \"Added\", \"Correct\" instead of \"Correcting\" or \"Corrected\", \"Update\" instead of \"Updated\" or \"Updating\") for the title of this pull request. The instructions in the PR description when the PR was created should explain this. See https://cbea.ms/git-commit for why PR and commit titles are important."
    comment_id: "title_imperative"
    vote: wait

  # Check the PR description.
  - description_pattern: '^.*DELETE THESE COMMENTS'
    comment: "Please remove the comments in the description that should be removed, as they explain. Otherwise, they will appear in email notifications and in the commit once the pull request has been merged."
    vote: REJECT

  # Avoid `string.IsNullOrEmpty` in C#.
  - path_pattern: '^.*\.cs$'
    diff_pattern: '^\s*.*\b[Ss]tring\.IsNullOrEmpty\('
    vote: wait
    comment: "Suggestion: only worry about `null` strings.\n\nIt's usually simpler not to worry about empty strings and just leave them be since they're usually rare. It's fine to add specific checks for `null` strings, but it's usually not worth the effort to check for empty ones and handling them in a special way. If something wants to be weird and give an empty string, then let it, good luck to it. If we are concerned about empty strings, then we should be just as concerned about strings with whitespace only and we can use `string.IsNullOrWhiteSpace(...)` instead of `string.IsNullOrEmpty(...)`."
    comment_id: "string_IsNullOrEmpty"

  # If snake_case is used in a C# file, then add a comment and vote to wait for the author.
  # Ideally, code formatting rules would enforce this,
  # but it's still nice point it out clearly in the PR or to automatically vote to wait so that the PR doesn't clutter your list of PRs to review.
  - path_pattern: '^.*\.cs$'
    diff_pattern: '^\s*(int|long|string|var) \S+_\S+'
    comment: "Automated comment: Please use camelCase for variables and not snake_case. It's important to have consistent and easy to read code as many people contribute to and maintain this repository."
    comment_id: "snake_case"
    vote: wait

  # Require a reviewer based on the title.
  - title_pattern: '(?i)^.*\[bug fix]'
    require: <ID>

  # Add a tag based on the title.
  - title_pattern: '(?i)^.*\[hot fix]'
    add_tags:
      - "hot fix"

  # Add a tag and change the title based on the path of any changed files.
  # "{TITLE}" will automatically be replaced by the current title.
  - title_pattern: '^((?!\[project]).)+$'
    path_pattern: '^/project/'
    new_title: "[project]{TITLE}"
    add_tags:
      - "project"

  # Add a tag based on a prefix of the branch name.
  - source_ref_name_pattern: '^refs/heads/hotfix'
    target_ref_name_pattern: '^refs/heads/main'
    add_tags:
      - "hot fix"

  # REJECT based on policy evaluations (build checks).
  - policy_checks:
    - evaluation_checks:
      # See https://learn.microsoft.com/en-us/rest/api/azure/devops/policy/evaluations/list the API output for help with figuring out the JSON Paths.
      - json_path: '$.configuration.settings.displayName'
        pattern: '^CI Build$'
      - json_path: '$.context.buildOutputPreview.jobName'
        pattern: '^(Build|Job)$'
      - json_path: '$.context.buildOutputPreview.taskName'
        pattern: '^(Build Library|Check Code Formatting|Limit Build Warnings|Lint.*|Test)$'
      - json_path: '$.status'
        pattern: '^rejected$'
    vote: REJECT

  # Requeue a build if policy evaluations (build checks) pass.
  - is_draft: false
    # Just enable for a few authors.
    author_pattern: '(?i)^Justin '
    policy_checks:
      - evaluation_checks:
        - json_path: '$.configuration.type.display_name'
          pattern: '^Work item linking$'
        - json_path: '$.status'
          pattern: '^approved$'
      - evaluation_checks:
        - json_path: '$.configuration.type.display_name'
          pattern: '^Required reviewers$'
        - json_path: '$.status'
          pattern: '^(?:approved|queued)$'
      - evaluation_checks:
        - json_path: '$.configuration.type.display_name'
          pattern: '^Comment requirements$'
        - json_path: '$.status'
          pattern: '^approved$'
      - evaluation_checks:
        - json_path: '$.configuration.type.display_name'
          pattern: '^Minimum number of reviewers$'
        - json_path: '$.status'
          pattern: '^approved$'
      - evaluation_checks:
        - json_path: '$.configuration.settings.displayName'
          pattern: '^CI Build$'
        - json_path: '$.status'
          # Do not requeue rejected builds because important tests might have failed and could fail again which wastes CI resources.
          # 'approved' should be it passed.
          # 'running' should mean it's already running.
          pattern: '^queued$'
    # The check to re-queue:
    requeue:
      - json_path: '$.configuration.settings.displayName'
        pattern: '^CI Build$'
    requeue_comment: "Automated comment: Re-queued \"CI Build\" using https://github.com/juharris/code-reviewer."
```

# Running
Run the script:
```bash
CR_ADO_PAT='YOUR PAT' python src/run.py config_path.yml
```

You can also use a config file from a URL (must start with "https://" or "http://"):
```bash
CR_ADO_PAT='YOUR PAT' python src/run.py https://mysite.com/config.yml
```

The script will reload the config file for each run.
A run happens when the script is started and then every `wait_after_review_s` seconds.

# Testing

Install `pytest`:
```bash
pip install pytest
```

Run the automated tests:
```bash
PYTHONPATH=src pytest
```
