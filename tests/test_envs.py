import os
import shutil
import tempfile
import unittest

from mock import patch

from component_builder.component import Component
from component_builder.envs import set_envs


@patch('component_builder.build.os.environ', {
    'CENTRAL_REPORT_LOCATION': '/reports',
    'RELEASE_TAG': '0.1'
})
class TestSetEnvs(unittest.TestCase):

    def setUp(self):
        self.appdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.appdir)
        os.makedirs(os.path.join(self.appdir, 'dummy-app', 'adi', 'envs'))
        name = os.path.join(self.appdir, 'dummy-app', 'adi', 'envs', 'circle')
        with open(name, 'w') as f:
            f.write('ANOTHER_VAR=$CIRCLE_MAGIC\n')
        self.dummy_app = Component(
            'dummy-app', downstream=['dummy-integration'],
            path=os.path.join(self.appdir, 'dummy-app'))
        self.dummy_integration = Component(
            'dummy-integration',
            path=os.path.join(self.appdir, 'dummy-integration'))

    def test_provides_dict_of_env_strings(self):
        set_envs([self.dummy_app, self.dummy_integration])

        self.assertEqual(
            sorted(self.dummy_app.env_string.split(' ')),
            ['DOCKER_IMAGE=dummy-app', 'DOCKER_TAG=0.1',
             'REPORT_LOCATION=/reports/dummy-app']
        )

    def test_provides_images_to_downstream_dependents(self):
        set_envs([self.dummy_app, self.dummy_integration])

        self.assertEqual(
            sorted(self.dummy_integration.env_string.split(' ')),
            ['DOCKER_IMAGE=dummy-integration',
             'DOCKER_TAG=0.1',
             'DUMMY_APP_DOCKER_IMAGE=dummy-app:0.1',
             'REPORT_LOCATION=/reports/dummy-integration']
        )

    def test_uses_env_dependent_variables_defined_by_component(self):
        os.environ['CIRCLECI'] = "1"

        set_envs([self.dummy_app, self.dummy_integration])
        self.assertEqual(
            sorted(self.dummy_app.env_string.split(' ')),
            ['ANOTHER_VAR=$CIRCLE_MAGIC', 'DOCKER_IMAGE=dummy-app',
             'DOCKER_TAG=0.1', 'REPORT_LOCATION=/reports/dummy-app']
        )

    def test_uses_local_variables_script_if_not_on_circle(self):
        del os.environ['CIRCLECI']
        local_filename = os.path.join(
            self.appdir, 'dummy-app', 'adi', 'envs', 'local')
        with open(local_filename, 'w') as f:
            f.write('LOCAL_VAR=buildermagic\n')
        self.addCleanup(os.remove, local_filename)

        set_envs([self.dummy_app, self.dummy_integration])

        self.assertEqual(
            sorted(self.dummy_app.env_string.split(' ')),
            ['DOCKER_IMAGE=dummy-app',
             'DOCKER_TAG=0.1',
             'LOCAL_VAR=buildermagic',
             'REPORT_LOCATION=/reports/dummy-app']
        )
