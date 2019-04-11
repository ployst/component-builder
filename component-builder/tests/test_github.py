import unittest

import six
from mock import Mock, patch

import github3

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


class TestUpdateBranch(unittest.TestCase):

    @patch('component_builder.github.get_sha')
    @patch('component_builder.github.get_repo')
    def test_forces_update_on_existing_branch(self, get_repo, get_sha):
        ref_mock = Mock()
        repo = Mock()
        repo.ref.return_value = ref_mock
        get_repo.return_value = repo
        branch_name = 'some-branch'
        sha = 'some-sha'
        get_sha.return_value = sha

        github.update_branch(branch_name)

        repo.ref.assert_called_once_with('heads/{0}'.format(branch_name))
        ref_mock.update.assert_called_once_with(sha, force=True)

    @patch('component_builder.github.get_sha')
    @patch('component_builder.github.get_repo')
    def test_creates_missing_branch(self, get_repo, get_sha):
        repo = Mock()
        repo.ref.side_effect = github3.exceptions.NotFoundError(Mock())
        get_repo.return_value = repo
        branch_name = 'some-branch'
        sha = 'some-sha'
        get_sha.return_value = sha

        github.update_branch(branch_name)

        repo.ref.assert_called_once_with('heads/{0}'.format(branch_name))
        repo.create_ref.assert_called_once_with(
            'refs/heads/{0}'.format(branch_name), sha)
