import unittest
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
from textwrap import dedent

from component_builder.component import Component, Tree
from component_builder.config import read_component_configuration


class TestDependencyTree(unittest.TestCase):
    def setUp(self):
        self.a1 = Component('a1', '')
        self.b1 = Component('b1', '')
        self.c1 = Component('c1', '', upstream=['a1', 'b1', 'd1'])
        self.d1 = Component('d1', '', upstream=['c2', 'b2'])
        self.a2 = Component('a2', '')
        self.b2 = Component('b2', '', upstream=['a2'])
        self.c2 = Component('c2', '')

    def test_hierarchy_correct(self):
        self.assertEqual(
            Tree.ordered([self.a2]),
            [self.a2, self.b2, self.d1, self.c1]
        )
        self.assertEqual(
            Tree.ordered([self.a1]),
            [self.a1, self.c1]
        )

    def test_hierarchy_correct_for_same_tree_different_layers(self):
        self.assertEqual(
            Tree.ordered([self.c1, self.a1]),
            [self.a1, self.c1]
        )

        self.assertEqual(
            Tree.ordered([self.c1, self.a2]),
            [self.a2, self.b2, self.d1, self.c1]
        )

    def test_hierarchy_in_layers_for_multiple_trees(self):
        self.assertEqual(
            Tree.ordered([self.a1, self.a2]),
            [self.a1, self.a2, self.b2, self.d1, self.c1]
        )

        self.assertEqual(
            Tree.ordered([self.c2, self.b2]),
            [self.c2, self.b2, self.d1, self.c1]
        )

        self.assertEqual(
            Tree.ordered([self.d1, self.a1, self.a2]),
            [self.a2, self.b2, self.d1, self.a1, self.c1]
        )


class TestDependencies(unittest.TestCase):

    def setUp(self):
        s = StringIO(dedent(
            u"""
            [ui]
            path=ui

            [service-A]
            path=service-a

            [integration]
            path=integration
            upstream=service-A,ui

            [super-integration]
            path=super-integration
            upstream=integration
            """))
        self.components = read_component_configuration(s)

    def test_include_downstream_dependencies(self):
        dep_ordered = Tree.ordered([self.components['service-A']])
        self.assertEqual(
            [d.title for d in dep_ordered],
            ['service-A', 'integration', 'super-integration']
        )

    def test_downstream_dependencies_at_the_end(self):
        dep_ordered = Tree.ordered(
            [self.components['integration'],
             self.components['service-A'],
             ]
        )
        self.assertEqual(
            [d.title for d in dep_ordered],
            ['service-A', 'integration', 'super-integration']
        )

    def test_get_upstream_builds(self):
        upstream = self.components['integration'].get_upstream_builds()
        self.assertEqual(
            sorted([d.title for d in upstream]),
            ['service-A', 'ui']
        )


class TestDownstreamLabel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        s = StringIO(dedent(
            u"""
            [ui]
            path=ui

            [service-A]
            path=service-a

            [integration]
            path=integration
            upstream=service-A,ui

            [super-integration]
            path=super-integration
            upstream=integration

            [other-thing]
            path=other-thing

            [circular-a]
            path=a
            upstream=circular-b

            [circular-b]
            path=b
            upstream=other-thing,circular-a
            """))
        cls.components = read_component_configuration(s)

    def test_upstream_components_have_their_downstream_components(self):
        self.assertEqual(
            self.components['ui'].ini['downstream'],
            ['integration', 'super-integration'])

    def test_downstream_components_dont_have_downstream_components(self):
        self.assertEqual(
            self.components['super-integration'].ini['downstream'],
            [])

    def test_handles_circular_references(self):
        self.assertEqual(
            self.components['circular-b'].ini['downstream'],
            ['circular-a']
        )
        self.assertEqual(
            self.components['circular-a'].ini['downstream'],
            ['circular-b']
        )
