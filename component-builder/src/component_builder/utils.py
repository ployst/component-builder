import subprocess

from bash import bash as bash_graceful

from . import exceptions


class bash(bash_graceful):

    def bash_with_captured_and_potentially_exposed_output(
            self, cmd, *args, **kwargs):
        stdout = kwargs.get('stdout', None)
        stderr = kwargs.get('stderr', None)
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        kwargs['sync'] = False

        ret = super(bash, self).bash(cmd, *args, **kwargs)
        output_out = []

        while True:

            outline = ret.p.stdout.readline()
            outline = outline

            if not outline:
                break

            output_out.append(outline)
            if stdout:
                stdout.write(outline.decode('utf_8'))

        self.stdout = b''.join(output_out)
        self.stderr = ret.p.stderr.read()
        if stderr:
            stderr.write(self.stderr.decode('utf_8'))
        self.code = ret.p.wait()

        if self.code != 0:
            raise exceptions.SubscriptException(
                self, cmd, ''.join(self.stderr))

        return self

    def bash(self, cmd, *args, **kwargs):
        return self.bash_with_captured_and_potentially_exposed_output(
            cmd, *args, **kwargs
        )


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
