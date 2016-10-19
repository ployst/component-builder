import os
import sys

from bash import bash


def convert_dict_to_env_string(envdict):
    env_list = ["{0}={1}".format(k, v) for k, v in envdict.items()]
    env_string = ' '.join(env_list)
    return env_string


def make(path, cmd, envs="", options="", output_console=False):
    makefile = os.path.join(path, 'Makefile')
    full_cmd = '{envs} make -f {0} {1} {2}'.format(
        makefile, options, cmd, envs=envs)
    bashkw = {}

    if output_console:
        bashkw = {'stdout': sys.stdout, 'stderr': sys.stderr}

    return bash(full_cmd, **bashkw)
