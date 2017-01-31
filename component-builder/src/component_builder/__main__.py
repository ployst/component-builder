import json
import sys

from docopt import docopt

from . import build, discover, envs, github, release

USAGE = """
Intelligent builder for working with component-based repositories

Usage:
  compbuild discover [--with-versions] {common}
  compbuild declare [<component>...] {common}
  compbuild build [<component>...] {common}
  compbuild test [<component>...] {common}
  compbuild label <label> [<component>...] {common}
  compbuild tag [<component>...] {common}
  compbuild release [<component>...] {common}
  compbuild get <attr> [<component>...] {common}
  compbuild env [<component>...] {common}
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
  --vs-branch=BRANCH   Discover changes made compared to BRANCH. If not set,
                       comparison will be to latest staging branch for each
                       component.
  --exclude-downstream  Only include directly changed things, not things that
                        declare them as upstreams.


""".format(
    common=('[--vs-branch=BRANCH] [--all] [--exclude-downstream] '
            '[--filter=SELECTOR ...] [--conf=FILE]')
)


def cli(out=sys.stdout):
    arguments = docopt(USAGE, version='1.0')

    b = build.Builder(arguments['--conf'])
    b.configure()

    selectors = set()
    filters = arguments['--filter']
    for fltr in filters:
        selectors.update(fltr.split(','))
    selectors = list(selectors)

    components = discover.run(
        b.components,
        arguments.get('<component>', []),
        arguments['--all'],
        compare_branch=arguments['--vs-branch'],
        selectors=selectors,
        include_downstream=not arguments['--exclude-downstream']
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
    elif arguments['declare']:
        build.declare_components_usage(components)
    elif arguments['build']:
        b.pre('build', components)
        build.run('build', components)
        b.post('build', components)
    elif arguments['test']:
        b.pre('test', components)
        build.run('test', components)
        b.post('test', components)
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
    elif arguments['get']:
        tmpl = u"{title}:{attr}"
        for c in components:
            value = c.ini.get(arguments['<attr>'], "")
            if isinstance(value, list):
                value = ','.join(value)
            out.write(
                tmpl.format(
                    title=c.title,
                    attr=value) + '\n'
            )


if __name__ == '__main__':
    cli()
