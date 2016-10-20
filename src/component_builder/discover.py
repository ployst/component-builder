from .component import Tree
from .utils import bash


def get_changed(candidates, branch=None):

    def is_changed(candidate):
        name = branch or candidate.branch_name('stable')

        b = bash('git log --oneline origin/{branch}..HEAD '
                 '-- {0} || echo "1"'.format(candidate.path, branch=name))
        return b.value().strip() != ''
    return filter(is_changed, candidates)


def run(components, label_filter=None, get_all=False):
    "Get paths and titles of changed components"
    if label_filter and get_all:
        print("Asked to filter and get all. Assuming filter...")
    if label_filter:
        candidates = [components[x] for x in label_filter]
    else:
        candidates = components.values()
        if not get_all:
            candidates = get_changed(candidates)
        candidates = Tree.ordered(candidates)
    return candidates
