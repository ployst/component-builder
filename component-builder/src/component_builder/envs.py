import os

from .utils import make


def ensure_report_location(comp_name):
    report_location = os.path.join(
        os.environ.get('CENTRAL_REPORT_LOCATION', '/tmp'), comp_name
    )
    try:
        os.mkdir(report_location)
    except OSError:
        pass
    return report_location


def env_dependent_overrides(component):
    envvars = {}

    override_filename = os.path.join(
        component.path, 'envs', os.environ.get('ENVIRONMENT', 'local')
    )
    if os.path.exists(override_filename):
        with open(override_filename, 'r') as f:
            for line in f.read().splitlines():
                line = line.strip()
                if line.startswith('#'):
                    continue
                key, value = line.split('=')
                envvars[key] = value
    return envvars


def get_version(component):
    b = make(
        component.path,
        'version',
        envs='BUILD_IDENTIFIER={0}'.format(os.environ['BUILD_IDENTIFIER']),
        options='--silent',
    )
    if b.code != 0:
        raise Exception('Version errored: {0}'.format(b.stderr))
    return b.value()


def set_envs(components):
    """
    Given a list of components, get the environment in which they should run.

    Return a dictionary of component name to string that can be prepended to
    a script run.
    """
    env_dict = {}
    for comp in components:
        comp_name = comp.title
        report_location = ensure_report_location(comp_name)
        version = get_version(comp)
        comp_env_dict = {
            'NAME': comp_name,
            'DOCKER_IMAGE': comp_name,
            'DOCKER_TAG': version,
            'REPORT_LOCATION': report_location,
            'VERSION': version,
        }

        comp_env_dict.update(env_dependent_overrides(comp))

        integration_dict = {}

        for upstream in comp.get_upstream_builds():
            upstream_env = env_dict.get(upstream.title)
            if not upstream_env:
                continue
            key = upstream.title.replace('-', '_').upper() + '_DOCKER_IMAGE'
            val = "{DOCKER_IMAGE}:{DOCKER_TAG}".format(**upstream_env)
            integration_dict[key] = val
        comp_env_dict.update(integration_dict)

        env_dict[comp_name] = comp_env_dict
        comp.env = comp_env_dict
