import os
import sys

from bash import bash as bash_graceful

from . import build


class bash(bash_graceful):
    def bash(self, cmd, *args, **kwargs):
        ret = super(bash, self).bash(cmd, *args, **kwargs)
        if self.code != 0:
            raise Exception('Error running command {0}'.format(cmd))
        return ret


def run(components):
    for component in components:
        env = os.environ.copy()
        env.update(component.env)
        if component.release_process:
            if component.release_process == 'docker':
                bash('tag-push', stdout=sys.stdout, stderr=sys.stderr, env=env)
            elif component.release_process == 'custom':
                build.run('release', [component])
            else:
                raise Exception("Unsupported release process")
