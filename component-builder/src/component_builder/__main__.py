import json
import sys

from docopt import docopt

from . import build, discover, envs, github, release


USAGE = """
Intelligent builder for working with component-based repositories

Usage:
  compbuild discover [--with-versions] {common}
  compbuild build [<component>...] {common}
  compbuild env [<component>...] {common}
  compbuild release [<component>...] {common}
  compbuild test [<component>...] {common}
  compbuild tag [<component>...] {common}
  compbuild label <label> [<component>...] {common}
  compbuild <action> [<component>...] {common}
  compbuild -h | --help
  compbuild --version

Options:
  -h --help            Show this screen.
  --all                Do all the components
  --filter=SELECTOR    Filter components based on selector
                       (e.g. --filter=relase-process=docker)
  --version            Show version.
  --conf=FILE          Configuration file location [default: builder.ini]
  --with-versions      Print out all items of interest, with versions

""".format(
    common='[--all] [--filter=SELECTOR] [--conf=FILE]'
)


def cli(out=sys.stdout):
    arguments = docopt(USAGE, version='1.0')

    b = build.Builder(arguments['--conf'])
    b.configure()

    selectors = arguments['--filter']
    if selectors:
        selectors = selectors.split(',')

    components = discover.run(
        b.components,
        arguments.get('<component>', []),
        arguments['--all'],
        selectors,
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
    elif arguments['<action>']:
        b.custom(arguments['<action>'], components)


if __name__ == '__main__':
    cli()
