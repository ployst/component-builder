import unittest
from StringIO import StringIO
from textwrap import dedent

from component_builder.component import Component, Tree
from component_builder.config import read_component_configuration


class TestDependencyTree(unittest.TestCase):
    def setUp(self):
        Component.all = {}
        self.a1 = Component('a1', '', downstream=['c1'])
        self.b1 = Component('b1', '', downstream=['c1'])
        self.c1 = Component('c1', '',)
        self.d1 = Component('d1', '', downstream=['c1'])
        self.a2 = Component('a2', '', downstream=['b2'])
        self.b2 = Component('b2', '', downstream=['d1'])
        self.c2 = Component('c2', '', downstream=['d1'])

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
         """
            [ui]
            path=ui
            downstream=integration

            [service-A]
            path=service-a
            downstream=integration

            [integration]
            path=integration
            downstream=super-integration

            [super-integration]
            path=super-integration
            """))
        read_component_configuration(s)

    def test_include_downstream_dependencies(self):
        dep_ordered = Tree.ordered([Component.all['service-A']])
        self.assertEqual(
            [d.title for d in dep_ordered],
            ['service-A', 'integration', 'super-integration']
        )

    def test_downstream_dependencies_at_the_end(self):
        dep_ordered = Tree.ordered(
            [Component.all['integration'],
             Component.all['service-A'],
             ]
        )
        self.assertEqual(
            [d.title for d in dep_ordered],
            ['service-A', 'integration', 'super-integration']
        )

    def test_get_upstream_builds(self):
        upstream = Component.all['integration'].get_upstream_builds()
        self.assertEqual(
            sorted([d.title for d in upstream]),
            ['service-A', 'ui']
        )
