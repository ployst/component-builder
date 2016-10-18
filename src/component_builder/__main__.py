"""
Intelligent builder for working with component-based repositories

Usage:
  compbuild discover
  compbuild build [<component>...]
  compbuild test [<component>...]
  compbuild release [<component>...]
  compbuild tag
  compbuild -h | --help
  compbuild --version

Options:
  -h --help            Show this screen.
  --version            Show version.
"""
import os

from docopt import docopt

from . import build, conf, discover, envs, github, release


def cli():
    arguments = docopt(__doc__, version='1.0')

    conf.read_component_configuration(open('builder.ini'))

    components = discover.run(arguments.get('<component>', []))
    envs.set_envs(components)

    if arguments['discover']:
        print("\n".join(c.title for c in components))
    elif arguments['build']:
        build.run('build', components)
    elif arguments['test']:
        build.run('test', components)
    elif arguments['tag']:
        github.create_tag(os.environ['RELEASE_TAG'])
    elif arguments['release']:
        release.run(components)

if __name__ == '__main__':
    cli()
