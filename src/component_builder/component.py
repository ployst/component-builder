from .utils import convert_dict_to_env_string


class Component(object):

    all = {}

    def __init__(self, title, path, release_process='', downstream=None):
        """
        title: Name of the component. Used for docker images and more...
        path: Path to the component (within which a makefile will be found)
        release_process: Type of release process. Supported are 'docker' or
                         'custom'. In the future, pypi. Leave blank if no
                         release required.
        downstream: List of components that rely on this one.
        """
        self.title = title
        self.downstream = downstream or []
        self.release_process = release_process
        self.env = {}
        self.all[title] = self
        self.path = path

    @property
    def env_string(self):
        return convert_dict_to_env_string(self.env)

    def get_upstream_builds(self):
        upstream = []
        for component in self.all.values():
            if self.title in component.downstream:
                upstream.append(component)
                upstream.extend(component.get_upstream_builds())
        return upstream

    def get_downstream_builds(self):
        downstream = []
        for ds in self.downstream:
            component = self.all[ds]
            downstream.append(component)
            downstream.extend(component.get_downstream_builds())
        return downstream

    def __repr__(self):
        return "<Component: {0}>".format(self.title)


class Tree(object):

    @classmethod
    def merge_branches(cls, *branches):
        if len(branches) > 1:
            left = branches[0]
            right = branches[1]
            rest = branches[2:]
            left_root = left[0]

            if left_root in right:
                first = right
                second = left
            else:
                first = left
                second = right

            merged = []
            for item in first:
                if item not in second:
                    merged.append(item)
            for item in second:
                if item not in merged:
                    merged.append(item)

            return cls.merge_branches(merged, *rest)
        return branches[0]

    @classmethod
    def ordered(cls, root_candidates):
        branches = []

        for c in root_candidates:
            branch = [c] + [c for c in c.get_downstream_builds()]
            branches.append(branch)

        return cls.merge_branches(*branches)
