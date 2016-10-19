"""
Intelligent builder for working with component-based repositories

Usage:
  compbuild discover
  compbuild build [<component>...]
  compbuild env [<component>...]
  compbuild release [<component>...]
  compbuild test [<component>...]
  compbuild tag [<component>...]
  compbuild label <label> [<component>...]
  compbuild -h | --help
  compbuild --version

Options:
  -h --help            Show this screen.
  --version            Show version.
"""
import json

from docopt import docopt

from . import build, discover, envs, github, release


def cli():
    arguments = docopt(__doc__, version='1.0')

    b = build.Builder()
    b.configure()

    components = discover.run(b.components, arguments.get('<component>', []))
    envs.set_envs(components)

    if arguments['discover']:
        print("\n".join(c.title for c in components))
    elif arguments['build']:
        build.run('build', components)
    elif arguments['test']:
        build.run('test', components)
    elif arguments['tag']:
        for comp in components:
            github.create_tag(comp.env['VERSION'])
    elif arguments['label']:
        for comp in components:
            github.update_branch(comp.branch_name(arguments['<label>']))
    elif arguments['release']:
        release.run(components)
    elif arguments['env']:
        print("\n".join(json.dumps(c.env, indent=4) for c in components))

if __name__ == '__main__':
    cli()
