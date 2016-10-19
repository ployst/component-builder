import os
import sys

from . import build, github
from .utils import bash


def run(components):
    for component in components:
        if not component.release_process:
            print("{0}: doesn't support releasing".format(component.title))
            continue
        env = os.environ.copy()
        env.update(component.env)
        if component.release_process == 'docker':
            bash('tag-push', stdout=sys.stdout, stderr=sys.stderr, env=env)
        elif component.release_process == 'custom':
            build.run('release', [component])
        else:
            raise Exception("Unsupported release process")

        github.update_branch(comp.branch_name('released'))
