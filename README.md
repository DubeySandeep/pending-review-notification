# `pending-review-notification` GitHub Action

Action to send notifications to reviewers on github-discussion when they miss reviewing PRs within expected time.

## Table of Contents

* [Usage](#usage)
* [Inputs](#inputs)

## Usage

1. Create a workflow file in the `.github/workflows/` dir.
**Example:**
```yaml
name: Send pending review notifications to reviewer on github-discussion
on:
  schedule:
    - cron: '0 0 * * 2,5'
permissions:
  pull-requests: read
  issues: read
  discussions: write

jobs:
  send_notifications:
    name: Send pending review notifications
    runs-on:  ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-18.04]
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.7'
          architecture: 'x64'
      - uses: DubeySandeep/pending-review-notification
        with:
          team-slur: << TEAM_SLUR >>
          repo-token: ${{secrets.GITHUB_TOKEN}}
          review-turnaround-hours: << TURNAROUND_HOURS >>
```
**Important notes:**
  - Replace `<< TEAM_SLUR >>` & `<< TURNAROUND_HOURS >>` with the team name and expected PR review time.
  - The [POSIX cron syntax](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html#tag_20_25_07) needs to quoted as * is a special character in YAML.


2. Add PENDING_REVIEW_NOTIFICATION_TEMPLATE.yml file in `.github/` dir.
Example:
```
Hi {{ username }},

It looks like you haven't reviewed the following PRs within the expected time:
{{ pr_list }}

Can you please review the pending PRs as soon as possible?

Please make sure to reply to this thread once all the PRs are reviewed!
```
**Important notes:**
  - Template can have `username` and  `pr_list` placeholders which will eventually get replaces with the reviewer's username and the list of PRs waiting on their review.

## Inputs

| Name          | Requirement | Default | Description |
| ------------- | ----------- | ------- | ----------- |
| `team-slur`               | _required_  | | The name of the team where discussion thread will be created.|
| `repo-token`              | _required_  | | The github-personal-token which atleast have rights to create a discussion in the given team. |
| `review-turnaround-hours` | _required_  | | The maximum review turnaround hours. Notifications will be sent only for PRs waiting for more than review-turnaround-hours.|


## License

See [LICENSE](LICENSE).
