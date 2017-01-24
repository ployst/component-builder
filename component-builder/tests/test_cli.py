import os
import unittest
from io import StringIO
from os.path import abspath, dirname, join

from mock import patch

from component_builder.__main__ import cli

TEST_BUILDER_CONF = abspath(
    join(dirname(__file__), 'dummy-single-repo', 'builder.ini')
)


def setup_changed_file(testcase, component):
    local_file = join(dirname(TEST_BUILDER_CONF),
                      component + '/Makefile')
    orig_content = open(local_file, 'r').read()

    def write_to_file(filename, content):
        with open(filename, 'w') as new:
            new.write(content)

    test_makefile = (
        '#test data from test_discover_local_uncommitted_changes_count'
        '\n\n'
        'version:\n'
        '\techo "1.5.${BUILD_IDENTIFIER}"'
    )
    write_to_file(
        local_file,
        test_makefile
    )
    testcase.addCleanup(write_to_file, local_file, orig_content)


@patch('component_builder.build.os.environ', {
    'BUILD_IDENTIFIER': '1'
})
class TestCli(unittest.TestCase):

    @patch('sys.argv', ['compbuild', 'discover', '--all', '--with-versions',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_with_versions(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            '\n'.join([
                'dummy-app:5.4.1',
                'dummy-integration:2.0.1',
                'dummy-island-service:1.5.1',
                ''
            ])
        )

    @patch('sys.argv', ['compbuild', 'discover', '--all',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_without_versions(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            '\n'.join([
                'dummy-app',
                'dummy-integration',
                'dummy-island-service',
                ''
            ])
        )

    @patch('sys.argv', ['compbuild', 'discover', '--all',
                        '--filter=release-process=docker',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_filter_by_one_key(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            '\n'.join([
                'dummy-app',
                'dummy-island-service',
                ''
            ])
        )

    @patch('sys.argv', ['compbuild', 'discover', '--all',
                        '--filter=release-process=docker,label=app',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_filter_by_multiple_keys(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            '\n'.join([
                'dummy-app',
                ''
            ])
        )

    @patch('sys.argv', ['compbuild', 'discover', '--all',
                        '--filter=release-process=docker,label!=app',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_filter_with_excludes_multiple_keys(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            '\n'.join([
                'dummy-island-service',
                ''
            ])
        )

    @patch('sys.argv', ['compbuild', 'discover', '--all',
                        '--filter=release-process=docker',
                        '--filter=label=app',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_filter_by_multiple_arguments(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            '\n'.join([
                'dummy-app',
                ''
            ])
        )

    @patch('sys.argv', ['compbuild', 'build', '--all',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_custom_commands(self):
        script_out = '/tmp/foo-out'
        try:
            os.remove(script_out)
        except OSError:
            pass

        cli()

        self.assertEqual(
            open(script_out).read(),
            "bar dummy-app\nbar dummy-integration\nbar dummy-island-service\n"
        )

    @patch('sys.argv', ['compbuild', 'discover', '--vs-branch=master',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_only_finds_changes(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            ''
        )

    @patch('sys.argv', ['compbuild', 'discover', '--vs-branch=master',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_discover_local_uncommitted_changes_count(self):
        setup_changed_file(self, 'dummy-island-service')
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            'dummy-island-service\n'
        )

    @patch('sys.argv', ['compbuild', 'get', 'label', '--all',
                        '--filter=release-process=docker',
                        '--filter=label=app',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    def test_get_ini_value(self):
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            'dummy-app:app\n'
        )


class TestCliDeclare(unittest.TestCase):

    def setUp(self):
        super(TestCliDeclare, self).setUp()
        setup_changed_file(self, 'dummy-app')

    @patch('component_builder.build.os.environ', {
        'BUILD_IDENTIFIER': '1',
        'INTERACT_WITH_GITHUB': 'anything',
        'PULL_REQUEST_NAMES': 'http://github.com/ployst/ployst/pulls/1',
    })
    @patch('sys.argv', ['compbuild', 'declare',
                        '--vs-branch=master',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    @patch('component_builder.build.github.add_pr_components_labels')
    def test_declare_calls_add_pr_components_labels_correctly(self, add_pr):
        s = StringIO()
        cli(out=s)

        add_pr.assert_called_once_with(
            'http://github.com/ployst/ployst/pulls/1',
            ['dummy-app', 'dummy-integration']
        )

    @patch('component_builder.build.os.environ', {'BUILD_IDENTIFIER': '1'})
    @patch('sys.argv', ['compbuild', 'declare',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    @patch('component_builder.build.github.add_pr_components_labels')
    def test_declare_does_not_call_add_pr_components_labels(self, add_pr):
        s = StringIO()
        cli(out=s)

        add_pr.assert_not_called()

    @patch('component_builder.build.os.environ', {
        'BUILD_IDENTIFIER': '1',
        'INTERACT_WITH_GITHUB': 'anything',
        'PULL_REQUEST_NAMES': 'http://github.com/ployst/ployst/pulls/1',
    })
    @patch('sys.argv', ['compbuild', 'declare',
                        '--vs-branch=master',
                        '--exclude-downstream',
                        '--conf={0}'.format(TEST_BUILDER_CONF)])
    @patch('component_builder.build.github.add_pr_components_labels')
    def test_exclude_downstream(self, add_pr):
        s = StringIO()
        cli(out=s)

        add_pr.assert_called_once_with(
            'http://github.com/ployst/ployst/pulls/1',
            ['dummy-app']
        )
