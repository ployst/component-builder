import os.path
import sys

from bash import bash

from . import config, github


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
                github.add_component_label(pr_url, title)


def command_exists(makefile, command):
    b = bash('make -f {0} -n {1}'.format(makefile, command))
    return b.code == 0


class Builder(object):
    def __init__(self, root_dir='.'):
        self.path = os.path.abspath(root_dir)

    def configure(self):
        config.read_component_configuration(
            open(os.path.join(self.path, 'builder.ini')),
            root=self.path
        )


def run(mode, components, status_callback=None, optional=False):
    errors = []

    for comp in components:
        declare_component_usage(comp.title)
        mark_commit_status(mode, comp.title, 'pending')

    for comp in components:
        comp_path = comp.path
        comp_name = comp.title
        print_message("{0}: {1}".format(mode, comp_name))
        # run build scripts in order they've been given.
        makefile = os.path.join(comp_path, 'Makefile')
        if optional and not command_exists(makefile, mode):
            print("Not available")
            continue
        cmd = '{envs} make -f {0} {1}'.format(
            makefile, mode, envs=comp.env_string)
        print(cmd)
        b = bash(cmd, stdout=sys.stdout, stderr=sys.stderr)
        if b.code != 0:
            errors.append(comp_name)
            mark_commit_status(mode, comp_name, 'error')
        else:
            mark_commit_status(mode, comp_name, 'success')

    if errors:
        raise BuilderFailure(mode, errors)
