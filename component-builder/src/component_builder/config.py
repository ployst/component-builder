from collections import OrderedDict
import os.path
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from .component import Component


def read_configuration(builder_ini_file, root='.'):
    config = ConfigParser(defaults={
        'upstream': '',
        'release-process': ''
    })
    config.readfp(builder_ini_file)
    component_config = OrderedDict()
    builder_config = {}

    for component in config.sections():
        ini_section_dict = dict(config.items(component))
        kwargs = {
            'title': component,
        }

        if 'compbuild' in component:
            subsection = component.split(':')[-1]
            builder_config[subsection] = kwargs
            builder_config[subsection].update(ini_section_dict)
        else:
            kwargs.update({
                'release_process': config.get(component, 'release-process'),
                'path': os.path.join(root, config.get(component, 'path')),
                'ini': ini_section_dict,
            })

            upstream = config.get(component, 'upstream')
            if upstream:
                kwargs['upstream'] = upstream.split(',')
            c = Component(**kwargs)
            component_config[c.title] = c

    return builder_config, component_config


def read_component_configuration(builder_ini_file, root='.'):
    _, component_config = read_configuration(
        builder_ini_file=builder_ini_file, root=root
    )
    return component_config
