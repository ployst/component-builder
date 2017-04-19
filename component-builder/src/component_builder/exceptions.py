class SubscriptException(Exception):
    def __init__(self, bash, cmd, output):
        self.bash = bash
        self.cmd = cmd
        self.output = output

    def __str__(self):
        return 'Error running command {0}:\n - {1}'.format(
            self.cmd, self.output)


class BuilderFailure(Exception):
    def __init__(self, mode, errors):
        super(BuilderFailure, self).__init__()
        self.error_components = errors
        self.mode = mode

    def __str__(self):

        comps = ", ".join([': '.join(ec) for ec in self.error_components])

        return ('{0} components failed to {1}: \n - {2}'.format(
            len(self.error_components), self.mode, comps)
        )
