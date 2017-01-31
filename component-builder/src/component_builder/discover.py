from functools import partial
from .component import Tree
from .utils import bash


def get_changed(candidates, branch=None):

    def is_changed(candidate):
        name = branch or candidate.branch_name('stable')
        git_differs = [
            'git diff --shortstat origin/{branch}...'.format(branch=name),
            'git diff HEAD'
        ]
        for differ in git_differs:
            cmd = ("{0} -- {1} || echo '1'".format(differ, candidate.path))
            b = bash(cmd)
            if b.value().strip() != '':
                return True
        return False
    return filter(is_changed, candidates)


def filter_by(selectors, components):

    def matches_selector(selector, component):
        sep = '='
        exclude = False
        if '!=' in selector:
            sep = '!='
            exclude = True

        key, value = selector.split(sep)

        component_value = component.ini.get(key)
        if exclude:
            if isinstance(component_value, list):
                return value not in component_value
            else:
                return component.ini.get(key) != value
        else:
            if isinstance(component_value, list):
                return value in component_value
            else:
                return component.ini.get(key) == value

    for selector in selectors:
        components = filter(partial(matches_selector, selector), components)

    return list(components)


def run(components, component_names=None, get_all=False, compare_branch=None,
        selectors=None, include_downstream=True):
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

        candidates = Tree.ordered(candidates, include_downstream)

    if selectors:
        candidates = filter_by(selectors, candidates)
    return candidates
