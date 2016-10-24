import os
from os.path import join, dirname
# import shutil
# import tempfile
import unittest

from mock import patch

from component_builder import config
from component_builder.build import Builder
from component_builder.component import Component, Tree
from component_builder.envs import set_envs


@patch('component_builder.build.os.environ', {
    'CENTRAL_REPORT_LOCATION': '/reports',
    'BUILD_IDENTIFIER': '0.1'
})
class TestSetEnvs(unittest.TestCase):

    def setUp(self):
        conf = join(dirname(__file__), 'dummy-single-repo', 'builder.ini')
        b = Builder(conf)
        self.components = b.configure()
        self.ordered_candidates = Tree.ordered(self.components.values())

    def test_provides_dict_of_env_strings(self):
        set_envs(self.ordered_candidates)

        self.assertEqual(
            sorted(self.components['dummy-island-service'].env_string.split(' ')),
            ['DOCKER_IMAGE=dummy-island-service', 'DOCKER_TAG=1.5.0.1',
             'REPORT_LOCATION=/reports/dummy-island-service',
             'VERSION=1.5.0.1']
        )

    def test_provides_images_to_downstream_dependents(self):
        set_envs(self.ordered_candidates)

        self.assertEqual(
            sorted(self.components['dummy-integration'].env_string.split(' ')),
            ['DOCKER_IMAGE=dummy-integration',
             'DOCKER_TAG=2.0.0.1',
             'DUMMY_APP_DOCKER_IMAGE=dummy-app:5.4.0.1',
             'REPORT_LOCATION=/reports/dummy-integration',
             'VERSION=2.0.0.1']
        )

    def test_uses_env_dependent_variables_defined_by_component(self):
        os.environ['ENVIRONMENT'] = "CI"

        set_envs(self.ordered_candidates)
        self.assertEqual(
            sorted(self.components['dummy-app'].env_string.split(' ')),
            ['ANOTHER_VAR=$CIRCLE_MAGIC', 'DOCKER_IMAGE=dummy-app',
             'DOCKER_TAG=5.4.0.1', 'REPORT_LOCATION=/reports/dummy-app',
             'VERSION=5.4.0.1']
        )

    def test_uses_local_variables_script_if_not_on_circle(self):
        del os.environ['ENVIRONMENT']
        set_envs(self.ordered_candidates)

        self.assertEqual(
            sorted(self.components['dummy-app'].env_string.split(' ')),
            ['DOCKER_IMAGE=dummy-app',
             'DOCKER_TAG=5.4.0.1',
             'LOCAL_VAR=buildermagic',
             'REPORT_LOCATION=/reports/dummy-app',
             'VERSION=5.4.0.1']
        )
