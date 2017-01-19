import six
import unittest

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

    def test_replace_labels(self):
        component_titles = ['library', 'service']
        current_labels = [
            Label('component:tool'), Label('component:service'),
            Label('not-a-component')]
        to_add, to_del = github.replace_labels(
            component_titles, current_labels)

        six.assertCountEqual(self, to_add, ['component:library'])
        six.assertCountEqual(self, to_del, ['component:tool'])
