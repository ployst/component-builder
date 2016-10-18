from ConfigParser import ConfigParser
from .utils import convert_dict_to_env_string


class Component(object):

    all = {}

    def __init__(self, title, path, release_process='', downstream=None):
        """
        title: Name of the component. Used for docker images and more...
        path: Path to the component (within which a makefile will be found)
        release_process: Type of release process. Supported are 'docker'. In
                         the future, pypi. Leave blank if no release required.
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

    def __repr__(self):
        return "<Component: {0}>".format(self.title)


def read_component_configuration():
    config = ConfigParser(defaults={
        'downstream': '',
        'release-process': ''
    })
    config.readfp(open('builder.ini'))

    for component in config.sections():
        kwargs = {
            'title': component,
            'release_process': config.get(component, 'release-process'),
            'path': config.get(component, 'path')
        }
        downstream = config.get(component, 'downstream')
        if downstream:
            kwargs['downstream'] = downstream.split(',')
        Component(**kwargs)

read_component_configuration()

COMPONENTS = Component.all
