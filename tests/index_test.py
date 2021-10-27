"""Unit test for the index.py file."""

import unittest
from datetime import datetime, timedelta, timezone
import json
from unittest.mock import patch, mock_open
import requests_mock

from src import index
from src import github_services


class ModuleIntegerationTest(unittest.TestCase):
    """Integeration test for the send notification feature."""
    def setUp(self):
        self.orgName = 'orgName'
        self.repoName = 'repo'
        self.pull_response =  [{
            'html_url': 'https://githuburl.pull/123',
            'number': 123,
            'title': 'PR title 1',
            'user': {
                'login': 'authorName',
            },
            'assignees': [{
                'login': 'reviewerName1',
            }, {
                'login': 'reviewerName2',
            }]
        }, {
            'html_url': 'https://githuburl.pull/234',
            'number': 234,
            'title': 'PR title 2',
            'user': {
                'login': 'authorName',
            },
            'assignees': [{
                'login': 'reviewerName1',
            }, {
                'login': 'reviewerName2',
            }]
        }]
        def get_past_time(hours=0):
            return (
                datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ")
        self.timeline1 = [{
            'event': 'created'
        }, {
            'event': 'assigned',
            'assignee': {
                'login': 'reviewerName1'
            },
            'created_at': get_past_time(hours=22)
        },{
            'event': 'assigned',
            'assignee': {
                'login': 'reviewerName2'
            },
            'created_at': get_past_time(hours=56)
        }]

        self.timeline2 = [{
            'event': 'created'
        }, {
            'event': 'assigned',
            'assignee': {
                'login': 'reviewerName1'
            },
            'created_at': get_past_time(hours=23)
        }, {
            'event': 'assigned',
            'assignee': {
                'login': 'reviewerName2'
            },
            'created_at': get_past_time(hours=19)
        }]

        self.test_template = "{{ username }}\n{{ pr_list }}"

    def mock_all_get_requests(self, mock_request):
        param_page_1='?page=1&per_page=100'
        param_page_2='?page=2&per_page=100'
        mock_request.get(
            github_services.PULL_REQUESTS_URL_TEMPLATE.format(
                self.orgName, self.repoName) + param_page_1,
            text=json.dumps(self.pull_response))
        mock_request.get(
            github_services.PULL_REQUESTS_URL_TEMPLATE.format(
                self.orgName, self.repoName) + param_page_2,
            text=json.dumps([]))

        mock_request.get(
            github_services.ISSUE_TIMELINE_URL_TEMPLATE.format(
                self.orgName, self.repoName, 123) + param_page_1,
            text=json.dumps(self.timeline1))
        mock_request.get(
            github_services.ISSUE_TIMELINE_URL_TEMPLATE.format(
                self.orgName, self.repoName, 123) + param_page_2,
            text=json.dumps([]))

        mock_request.get(
            github_services.ISSUE_TIMELINE_URL_TEMPLATE.format(
                self.orgName, self.repoName, 234) + param_page_1,
            text=json.dumps(self.timeline2))
        mock_request.get(
            github_services.ISSUE_TIMELINE_URL_TEMPLATE.format(
                self.orgName, self.repoName, 234) + param_page_2,
            text=json.dumps([]))

    def mock_post_discussion_request(self, mock_request):
        request = mock_request.post(
            github_services.CREATE_DISCUSSION_URL_TEMPLATE.format(
                self.orgName, 'teamName'),
            text=json.dumps({}))
        return request

    def test_executing_main_function_sends_notification(self):
        with requests_mock.Mocker() as mock_request:
            self.mock_all_get_requests(mock_request)
            request = self.mock_post_discussion_request(mock_request)
            file_data = mock_open(read_data=self.test_template)
            with patch("builtins.open", file_data):
                index.main([
                    '--team', 'teamName',
                    '--repo', 'orgName/repo',
                    '--max-wait-hours', '20',
                    '--token', 'githubTokenForApiRequest'
                ])
        self.assertTrue(request.called)
        self.assertEqual(request.call_count, 2)
        expected_messages = [
            {
                'title': '[@reviewerName1] Pending review on PRs',
                'body': '@reviewerName1\n- [#123](https://githuburl.pull/123) '
                    '[Waiting from the last 22 hours]\n'
                    '- [#234](https://githuburl.pull/234) '
                    '[Waiting from the last 23 hours]'
            },
            {
                'title': '[@reviewerName2] Pending review on PRs',
                'body': '@reviewerName2\n- [#123](https://githuburl.pull/123) '
                    '[Waiting from the last 2 days, 8 hours]'
            },
        ]
        self.assertEqual(
            request.request_history[0].json(), expected_messages[0])
        self.assertEqual(
            request.request_history[1].json(), expected_messages[1])
