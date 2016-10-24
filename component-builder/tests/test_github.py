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
