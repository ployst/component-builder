import os.path
from ConfigParser import ConfigParser

from .component import Component


def read_component_configuration(builder_ini_file, root='.'):
    config = ConfigParser(defaults={
        'downstream': '',
        'release-process': ''
    })
    config.readfp(builder_ini_file)
    components = {}
    for component in config.sections():
        kwargs = {
            'title': component,
            'release_process': config.get(component, 'release-process'),
            'path': os.path.join(root, config.get(component, 'path'))
        }
        downstream = config.get(component, 'downstream')
        if downstream:
            kwargs['downstream'] = downstream.split(',')
        c = Component(**kwargs)
        components[c.title] = c
    return components
