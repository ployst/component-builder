import json
import sys

from docopt import docopt

from . import build, discover, envs, exceptions, github, release

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
  --vs-branch=BRANCH   Discover changes made compared to BRANCH. If not set,
                       comparison will be to latest staging branch for each
                       component. Should be in the form `origin/master`. Can
                       also be a commit id to compare against.
  --exclude-downstream        Only include directly changed things, not things
                              that declare them as upstreams.
  --out=FILE                  Write make command output to FILE rather than
                              stdout.
  --github-status-name=NAME   The name/description to use as the commit status.
                              Defaults to "<command>".


""".format(
    common=('[--vs-branch=BRANCH] [--all] [--exclude-downstream] '
            '[--filter=SELECTOR ...] [--conf=FILE] [--out=FILE] '
            '[--github-status-name=NAME]')
)


def cli(out=sys.stdout, err=sys.stderr):
    arguments = docopt(USAGE, version='1.0')

    b = build.Builder(arguments['--conf'])
    b.configure()

    if arguments['--out']:
        out = open(arguments['--out'], 'w')

    selectors = set()
    filters = arguments['--filter']
    for fltr in filters:
        selectors.update(fltr.split(','))
    selectors = list(selectors)

    components = discover.run(
        b.components,
        arguments.get('<component>', []),
        arguments['--all'],
        compare_with=arguments['--vs-branch'],
        selectors=selectors,
        include_downstream=not arguments['--exclude-downstream']
    )
    envs.set_envs(components)
    try:
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
            build.run(
                'build', components,
                github_status_name=arguments['--github-status-name']
            )
            b.post('build', components)
        elif arguments['test']:
            b.pre('test', components)
            build.run(
                'test', components,
                github_status_name=arguments['--github-status-name']
            )
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
            out.write("\n".join(
                json.dumps(c.env, indent=4) for c in components)
            )
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
        elif arguments['<action>']:
            b.pre(arguments['<action>'], components)
            build.run(arguments['<action>'], components, make_options="-s",
                      make_output={'stdout': out, 'stderr': err},
                      github_status_name=arguments['--github-status-name'])
            b.post(arguments['<action>'], components)
    except exceptions.SubscriptException as e:
        print("FAILURE: {0}\n".format(e))
        sys.exit(1)
    except exceptions.BuilderFailure as e:
        print("FAILURE: {0}\n".format(e))
        sys.exit(1)

    if arguments['--out']:
        out.close()


if __name__ == '__main__':
    cli()
