from collections import OrderedDict
import os.path
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from .component import Component


def read_component_configuration(builder_ini_file, root='.'):
    config = ConfigParser(defaults={
        'upstream': '',
        'release-process': ''
    })
    config.readfp(builder_ini_file)
    components = OrderedDict()
    for component in config.sections():
        kwargs = {
            'title': component,
            'release_process': config.get(component, 'release-process'),
            'path': os.path.join(root, config.get(component, 'path'))
        }
        upstream = config.get(component, 'upstream')
        if upstream:
            kwargs['upstream'] = upstream.split(',')
        c = Component(**kwargs)
        components[c.title] = c
    return components
