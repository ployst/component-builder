import os

from .component import Component, Tree
from .utils import bash


def get_changed(candidates, branch=None):

    def is_changed(candidate):
        name = branch or candidate.branch_name('stable')

        b = bash('git log --oneline origin/{branch}..HEAD '
                 '-- {0} || echo "1"'.format(candidate.path, branch=name))
        return b.value().strip() != ''
    return filter(is_changed, candidates)


def run(components=None):
    "Get paths and titles of changed components"
    if components:
        candidates = [Component.all[x] for x in components]
    else:
        candidates = Component.all.values()
        candidates = get_changed(candidates)
        candidates = Tree.ordered(candidates)
    return candidates
