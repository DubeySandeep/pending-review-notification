import index
import json
import requests
import github_domain
import unittest

class TestClassGenerateMessage(unittest.TestCase):
    def test_generate_message_should_return_correct_message(self):

        message = index.generate_message('Nikhil', '1')
        expected_message = (
            'Hi @Nikhil,\n\nIt looks like you haven\'t reviewed the following '
            'PRs within the expected time:\n1\n\nCan you please review the '
            'pending PRs as soon as possible?\n\nPlease make sure to reply to '
            'this thread once all the PRs are reviewed!')

        self.assertEqual(expected_message, message)

class TestClassSendNotification(unittest.TestCase):
    def test_check_sending_notfications(self):
        link_to_mock_pr = (
            'https://api.github.com/repos/octocat/hello-world/pulls')

        response = requests.get(link_to_mock_pr)
        mock_prs_dict = json.loads(response.text)
        pull_requests = []
        for mock_pr in mock_prs_dict:
            pull_request = (
                github_domain.PullRequest.from_github_response(mock_pr))
            pull_requests.append(pull_request)
        index.send_notification('octocat', pull_requests, 'oppia', 'oppia')



