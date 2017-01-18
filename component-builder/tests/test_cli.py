from io import StringIO
import os
from os.path import abspath, dirname, join
import unittest

from mock import patch

from component_builder.__main__ import cli

TEST_BUILDER_CONF = abspath(
    join(dirname(__file__), 'dummy-single-repo', 'builder.ini')
)


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
        def setup_changed_file():
            local_file = join(dirname(TEST_BUILDER_CONF),
                              'dummy-island-service/Makefile')
            orig_content = open(local_file, 'r').read()
            def write_to_file(filename, content):
                with open(filename, 'w') as new:
                    new.write(content)

            test_makefile = (
                '#test data from test_discover_local_uncommitted_changes_count\n'
                '\n'
                'version:\n'
                '\techo "1.5.${BUILD_IDENTIFIER}"'
            )
            write_to_file(
                local_file,
                test_makefile
            )
            self.addCleanup(write_to_file, local_file, orig_content)

        setup_changed_file()
        s = StringIO()
        cli(out=s)

        self.assertEqual(
            s.getvalue(),
            'dummy-island-service\n'
        )
