import os.path
import sys

from . import config, exceptions, github
from .utils import component_script, make


def print_message(msg):
    length = 79
    line = '#' * length
    msg = (line + '\n' +
           '# {: <75} #\n'.format(msg) +
           line)
    print(msg)


def mark_commit_status(mode, component_name, status, github_status_name):
    if os.environ.get('INTERACT_WITH_GITHUB'):
        title = github_status_name or 'builder-{0}-{1}'.format(
            component_name, mode)
        description = "{0}: {1}".format(
            component_name, github_status_name or mode)
        return github.mark_status_for_component(
            title, description, component_name, status)


def declare_components_usage(components):
    if os.environ.get('INTERACT_WITH_GITHUB'):
        titles = [c.title for c in components]
        prs = os.environ.get('PULL_REQUEST_NAMES', '')
        for pr_url in prs.split(','):
            if pr_url:
                github.add_pr_components_labels(pr_url, titles)


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
        output = None
        # Ignore if running --xunit tests (identified by use of Tee)
        if sys.stdout.__class__.__name__ != 'Tee':
            output = {'stdout': sys.stdout, 'stderr': sys.stderr}

        if script_name:
            errors = []
            script_path = os.path.abspath(os.path.join(self.path, script_name))
            for comp in components:
                try:
                    component_script(
                        comp.path,
                        script_path,
                        envs=comp.env_string,
                        output=output,
                    )
                except exceptions.SubscriptException as e:
                    errors.append((comp.title, e.output))
            if errors:
                raise exceptions.BuilderFailure(script_name, errors)

    def pre(self, stage, components):
        return self.hook('pre-{}'.format(stage), components)

    def post(self, stage, components):
        return self.hook('post-{}'.format(stage), components)


def run(mode, components, status_callback=None, optional=False,
        make_options="", make_output=None, github_status_name=None):
    errors = []
    bashes = []
    for comp in components:
        mark_commit_status(mode, comp.title, 'pending', github_status_name)

    for comp in components:
        comp_name = comp.title
        print_message("{0}: {1}".format(mode, comp_name))
        # run build scripts in order they've been given.
        if optional and not command_exists(comp, mode):
            print("Not available")
            continue
        success = True
        if not make_output:
            # Ignore if running --xunit tests (identified by use of Tee)
            if sys.stdout.__class__.__name__ != 'Tee':
                make_output = {'stdout': sys.stdout, 'stderr': sys.stderr}
        try:
            b = make(
                comp.path, mode, envs=comp.env_string, options=make_options,
                output=make_output)
            bashes.append(b)
        except exceptions.SubscriptException as e:
            success = False
            errors.append((comp_name, e.output))
            mark_commit_status(mode, comp_name, 'error', github_status_name)

        if success:
            mark_commit_status(
                mode, comp_name, 'success', github_status_name)

    if errors:
        raise exceptions.BuilderFailure(mode, errors)

    return bashes
