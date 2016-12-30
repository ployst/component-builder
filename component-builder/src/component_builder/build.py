import os.path

from . import config, github
from .utils import make, component_script


class BuilderFailure(Exception):
    def __init__(self, mode, errors):
        super(BuilderFailure, self).__init__()
        self.error_components = errors
        self.mode = mode

    def __str__(self):
        comps = ", ".join(self.error_components)
        return ('{0} components failed to {1}: {2}'.format(
            len(self.error_components), self.mode, comps)
        )


def print_message(msg):
    length = 79
    line = '#' * length
    msg = (line + '\n' +
           '# {: <75} #\n'.format(msg) +
           line)
    print(msg)


def mark_commit_status(*args, **kwargs):
    if os.environ.get('INTERACT_WITH_GITHUB'):
        return github.mark_status_for_component(*args, **kwargs)


def declare_component_usage(title):
    if os.environ.get('INTERACT_WITH_GITHUB'):
        prs = os.environ.get('PULL_REQUEST_NAMES', '')
        for pr_url in prs.split(','):
            if pr_url:
                github.add_pr_component_label(pr_url, title)


def command_exists(component, command):
    b = make(component.path, command, envs="", options="-n")
    return b.code == 0


class Builder(object):
    def __init__(self, builder_file):
        self.builder_file = builder_file
        self.path = os.path.dirname(self.builder_file)

    def configure(self):
        self.config, self.components = config.read_configuration(
            open(self.builder_file), root=self.path
        )

        return self.components

    def hook(self, hook_name, components):
        script_name = self.config['hooks'].get(hook_name)
        if script_name:
            errors = []
            script_path = os.path.abspath(os.path.join(self.path, script_name))
            for comp in components:
                b = component_script(
                    comp.path,
                    script_path,
                    envs=comp.env_string,
                    output_console=False
                )
                if b.code != 0:
                    errors.append(comp.title)
            if errors:
                raise BuilderFailure(script_name, errors)

    def pre(self, stage, components):
        return self.hook('pre-{}'.format(stage), components)

    def post(self, stage, components):
        return self.hook('post-{}'.format(stage), components)


def run(mode, components, status_callback=None, optional=False):
    errors = []

    for comp in components:
        declare_component_usage(comp.title)
        mark_commit_status(mode, comp.title, 'pending')

    for comp in components:
        comp_name = comp.title
        print_message("{0}: {1}".format(mode, comp_name))
        # run build scripts in order they've been given.
        if optional and not command_exists(comp, mode):
            print("Not available")
            continue
        b = make(
            comp.path, mode, envs=comp.env_string, output_console=True)
        if b.code != 0:
            errors.append(comp_name)
            mark_commit_status(mode, comp_name, 'error')
        else:
            mark_commit_status(mode, comp_name, 'success')

    if errors:
        raise BuilderFailure(mode, errors)
