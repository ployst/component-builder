from bash import bash
import os

from .conf import COMPONENTS


def get_changed(candidates):
    def is_changed(candidate):
        b = bash('test $(git log origin/master..HEAD -- {0} '
                 '| wc -l) -gt 0'.format(candidate.path))
        return b.code == 0
    return filter(is_changed, candidates)


def get_dependency_ordered(candidates):
    for c in candidates:
        for downstream in c.downstream:
            if downstream not in [c2.title for c2 in candidates]:
                candidates.append(COMPONENTS[downstream])

    # TODO: Make this be a little cleverer (to not harcode 'integration-tests')
    def easy_sort(obj):
        # Just make sure integration-tests is at the end.
        if obj.title == 'integration-tests':
            return (1, obj.title)
        return (0, obj.title)

    return sorted(candidates, key=easy_sort)


def run(components=None):
    "Get paths and titles of changed components"
    if components:
        candidates = [COMPONENTS[x] for x in components]
    else:
        candidates = COMPONENTS.values()
        # If we're on master, we'll do everything.
        if os.environ.get('BRANCH_NAME', '') not in ('master',):
            candidates = get_changed(candidates)
        candidates = get_dependency_ordered(candidates)
    return candidates
