"The index file for sending pending-review notifications."

import argparse
import logging
import os
import re

from src import github_services

PARSER = argparse.ArgumentParser(
    description='Send pending review notifications to reviewers.')
PARSER.add_argument(
    '--token',
    type=str,
    help='The github-token to be used for creating github discussions.')
PARSER.add_argument(
    '--repo',
    type=str,
    help='The repository name for fetching the pull requests.')
PARSER.add_argument(
    '--team',
    type=str,
    help='The team name for sending notification through API.')
PARSER.add_argument(
    '--max-wait-hours',
    type=int,
    help='The maximum waiting time for getting a PR reviewed in hours.')
PARSER.add_argument(
    '--verbose',
    action='store_true',
    help='Whether to add important logs in the process.')


def generate_message(username, pr_list):
    """Generates message using the template provided in
    PENDING_REVIEW_NOTIFICATION_TEMPLATE.md file.
    """
    template_path = '.github/PENDING_REVIEW_NOTIFICATION_TEMPLATE.md'
    if not os.path.exists(template_path):
        raise Exception(
            'Please add a template on path: {0}'.format(template_path))
    message = ''
    with open(template_path, 'r') as file:
        message = file.read()

    message = re.sub(r'\{\{ *username *\}\}', '@' + username, message)
    message = re.sub(r'\{\{ *pr_list *\}\}', pr_list, message)

    return message


def send_notification(username, pull_requests, org_name, team_name):
    """Sends notification on github-discussion."""
    pr_list_messages = []
    for pull_request in pull_requests:
        assignee = pull_request.get_assignee(username)
        pr_list_messages.append(
            '- [#{0}]({1}) [Waiting from the last {2}]'.format(
                pull_request.number, pull_request.url,
                assignee.get_readable_waiting_time()))

    title = '[@{0}] Pending review on PRs'.format(username)
    body = generate_message(username, '\n'.join(pr_list_messages))

    github_services.create_discussion(org_name, team_name, title, body)


def main(args=None):
    """The main function to execute the workflow."""
    parsed_args = PARSER.parse_args(args=args)
    team_name = parsed_args.team
    org_name, repo = parsed_args.repo.split('/')
    max_wait_hours = parsed_args.max_wait_hours

    if parsed_args.verbose:
        logging.basicConfig(
            format='%(levelname)s: %(message)s', level=logging.INFO)

    github_services.init_service(parsed_args.token)

    reviewer_to_assigned_prs = github_services.get_prs_assigned_to_reviewers(
        org_name, repo, max_wait_hours)
    for reviewer_name, prs in reviewer_to_assigned_prs.items():
        send_notification(reviewer_name, prs, org_name, team_name)

    return 0


if __name__ == '__main__':
    main()
