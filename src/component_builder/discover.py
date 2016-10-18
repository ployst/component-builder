from bash import bash
import os

from .component import Component, Tree


def get_changed(candidates):
    def is_changed(candidate):
        b = bash('test $(git log origin/master..HEAD -- {0} '
                 '| wc -l) -gt 0'.format(candidate.path))
        return b.code == 0
    return filter(is_changed, candidates)


def run(components=None):
    "Get paths and titles of changed components"
    if components:
        candidates = [Component.all[x] for x in components]
    else:
        candidates = Component.all.values()
        # If we're on master, we'll do everything.
        if os.environ.get('BRANCH_NAME', '') not in ('master',):
            candidates = get_changed(candidates)
        candidates = Tree.ordered(candidates)
    return candidates
