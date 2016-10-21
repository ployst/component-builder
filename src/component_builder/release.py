import os
import sys

from . import build
from .utils import bash


def run(components):
    for component in components:
        if not component.release_process:
            print("{0}: doesn't support releasing".format(component.title))
            continue
        if component.release_process == 'docker':
            env = os.environ.copy()
            env.update(component.env)
            bash('tag-push', stdout=sys.stdout, stderr=sys.stderr, env=env)
        elif component.release_process == 'custom':
            build.run('release', [component])
        else:
            raise Exception("Unsupported release process")
