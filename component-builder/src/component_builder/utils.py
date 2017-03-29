import sys

from bash import bash as bash_graceful


class bash(bash_graceful):
    def bash(self, cmd, *args, **kwargs):
        ret = super(bash, self).bash(cmd, *args, **kwargs)
        if self.code != 0:

            raise Exception('Error running command {0}:\n{1}'.format(
                cmd, self.stderr)
            )
        return ret


def convert_dict_to_env_string(envdict):
    env_list = ["{0}={1}".format(k, v) for k, v in envdict.items()]
    env_string = ' '.join(env_list)
    return env_string


def make(path, cmd, envs="", options="", output=None):
    cmd = 'make {0} {1}'.format(options, cmd)
    return component_script(
        path=path, script=cmd, envs=envs, output=output
    )


def component_script(path, script, envs="", output=None):
    full_cmd = 'cd {path} && {envs} {0}'.format(
        script, path=path, envs=envs)
    bashkw = {}

    if output:
        bashkw = output

    return bash(full_cmd, **bashkw)
