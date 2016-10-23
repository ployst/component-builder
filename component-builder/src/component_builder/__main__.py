"""
Intelligent builder for working with component-based repositories

Usage:
  compbuild discover [--all] [--with-versions] [--conf=FILE]
  compbuild build [<component>...] [--all] [--conf=FILE]
  compbuild env [<component>...] [--all] [--conf=FILE]
  compbuild release [<component>...] [--all] [--conf=FILE]
  compbuild test [<component>...] [--all] [--conf=FILE]
  compbuild tag [<component>...] [--all] [--conf=FILE]
  compbuild label <label> [<component>...] [--all] [--conf=FILE]
  compbuild -h | --help
  compbuild --version

Options:
  -h --help            Show this screen.
  --all                Do all the components
  --version            Show version.
  --conf=FILE          Configuration file location [default: builder.ini]
  --with-versions      Print out all items of interest, with versions

"""
import json
import sys

from docopt import docopt

from . import build, discover, envs, github, release


def cli(out=sys.stdout):
    arguments = docopt(__doc__, version='1.0')

    b = build.Builder(arguments['--conf'])
    b.configure()

    components = discover.run(
        b.components,
        arguments.get('<component>', []),
        arguments['--all']
    )
    envs.set_envs(components)

    if arguments['discover']:
        tmpl = u"{title}"
        if arguments['--with-versions']:
            tmpl += u':{version}'
        for c in components:
            out.write(
                tmpl.format(title=c.title, version=c.env['VERSION']) + '\n'
            )
    elif arguments['build']:
        build.run('build', components)
    elif arguments['test']:
        build.run('test', components)
    elif arguments['tag']:
        for comp in components:
            github.create_tag("{0}-{1}".format(
                comp.title, comp.env['VERSION'])
            )
    elif arguments['label']:
        for comp in components:
            github.update_branch(comp.branch_name(arguments['<label>']))
    elif arguments['release']:
        release.run(components)
    elif arguments['env']:
        out.write("\n".join(json.dumps(c.env, indent=4) for c in components))

if __name__ == '__main__':
    cli()
