from functools import partial
from .component import Tree
from .utils import bash


def get_changed(candidates, branch=None):

    def is_changed(candidate):
        name = branch or candidate.branch_name('stable')

        b = bash('git log --oneline origin/{branch}..HEAD '
                 '-- {0} || echo "1"'.format(candidate.path, branch=name))
        return b.value().strip() != ''
    return filter(is_changed, candidates)


def filter_by(selectors, components):

    def matches_selector(selector, component):
        key, value = selector.split('=')
        return component.ini.get(key) == value

    for selector in selectors:
        components = filter(partial(matches_selector, selector), components)

    return list(components)


def run(components, component_names=None, get_all=False, compare_branch=None,
        selectors=None):
    "Get paths and titles of changed components"
    if component_names and get_all:
        print("Asked for specific components and get all. "
              "Assuming specific components...")
    if component_names:
        candidates = [components[x] for x in component_names]
    else:
        candidates = components.values()
        if not get_all:
            candidates = get_changed(candidates, compare_branch)
        candidates = Tree.ordered(candidates)

    if selectors:
        candidates = filter_by(selectors, candidates)
    return candidates
