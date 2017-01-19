import unittest

import six
from mock import Mock, patch

from component_builder import github


class TestValidatePRURL(unittest.TestCase):

    def test_true_for_valid_pr_urls(self):
        for valid in [
                'https://blah/1',
                'http://github.com/ployst/ployst/pulls/1']:
            self.assertTrue(github.validate_pr_url(valid),
                            '{0} is not valid'.format(valid))

    def test_false_for_invalid_pr_urls(self):
        for invalid in ['null', 'http://github.com/ployst/ployst', '']:
            self.assertRaises(
                github.ValidationError, github.validate_pr_url, invalid
            )


class Label(object):
    def __init__(self, name):
        self.name = name

    def name(self):
        return self.name


class TestAddPRComponentsLabels(unittest.TestCase):

    def setUp(self):
        self.component_titles = ['library', 'service']
        self.current_labels = [
            Label('component:tool'), Label('component:service'),
            Label('not-a-component')]

    def test_replace_labels(self):
        to_add, to_del = github.replace_labels(
            self.component_titles, self.current_labels)

        six.assertCountEqual(self, to_add, ['component:library'])
        six.assertCountEqual(self, to_del, ['component:tool'])

    @patch('component_builder.github.get_repo')
    def test_add_pr_components_labels(self, get_repo):
        issue = Mock()
        issue.labels.return_value = self.current_labels
        repo = Mock()
        repo.issue.return_value = issue
        get_repo.return_value = repo

        pr_url = 'http://github.com/ployst/ployst/pulls/1'
        github.add_pr_components_labels(pr_url, self.component_titles)

        repo.issue.assert_called_once_with('1')
        issue.labels.assert_called_once_with()
        issue.remove_label.assert_called_once_with('component:tool')
        issue.add_labels.assert_called_once_with('component:library')
        self.assertEqual(len(repo.method_calls), 1)
        self.assertEqual(len(issue.method_calls), 3)
