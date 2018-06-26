# Component Builder

A component builder suitable for building, testing and deploying services in
a single repo.

## Getting Started

1. Install component-builder from pypi:

    $ pip install component_builder

2. Create a repository with isolated components, each with its own directory

    ```
     $ ls services
     avatars    billing    notifications   user-api
    ```

3. Create a `builder.ini` file defining which components you'd like to auto build.

Place it in the root of your repository

    ```
     $ cat services/builder.ini
     [avatar-service]
     path=avatars

     [billing-service]
     path=billing

     [notification-service]
     path=notifications
     release-process=custom

     [user-api]
     path=user-api
     release-process=docker
    ```

4. Run commands! (or actually, modify your circle/travis/jenkins scripts to use
   the library)

## Component Definition

Any component defined in builder.ini will be treated as a first class citizen.

### Config

    path
        path to the component (in which a Makefile should be found)
    release-process
        If present docker|custom. If docker, compbuild will expect to find an
        image built locally (during the build phase) that it can push at the
        release point to a docker registry
    upstream
        A comma separated list of components that, if built, should trigger
        a build for this component. Useful for integration tests for
        example.

### Makefile

    `make version`
        Should echo a string defining this version of the component. This is
        used to tag the repo, to tag docker images for this component and should
        be used if making libraries.

        BUILD_IDENTIFIER is a useful environment variable passed in to this
        call which should be used to ensure a unique version on every
        releasable build

    `make build`
        Should do everything that is required so that testing and releasing can
        be performed.

    `make test`
        Run tests, syntax checkers etc.

    `make release` (optional)
        If `release-process` is defined as "custom", this will be called during
        `compbuild release`. Examples of things this might do:
            - Zip up package, place in known location for later step on build
              server to ship somewhere.
            - Release your library to pypi/npm

## Typical Flow

    $ compbuild declare
    $ compbuild build
    $ compbuild test
    $ compbuild label 'stable'
    $ compbuild tag
    $ compbuild release

Given the above repository, where a PR was made with changes to `user-api` and
`notifications`, this would do the following:

    - Run `make build` on each changed component (user-api and notifications only)
    - Run `make test` on changed components
    - Create/Update a branch on github named stable-user-api to point to this commit
    - Create/Update a branch on github named stable-notifications to point to this commit
    - Create a tag of notifications-${version} and user-api-${version}
    - Run `make release` on notifications
    - Push a docker image on behalf of user-api
    - Create/Update branches for both named released-notifications and released-user-api

Additionally:

 - github issue labels of component:notifications and component:user-api
   appear on the pull request
 - Commit statuses for the build + test phases of each component are added

## Alternative Flow

For more fine grained control, you can call any command with the names of the
components you want to perform that action on.

## CI

### Environment Variables

The build system is responsible for providing env variables to configure component-builder

BUILD_IDENTIFIER
    Unique identifier of the current build

CENTRAL_REPORT_LOCATION
    A local directory that per component reports should be written to.

ENVIRONMENT (local|CI|etc..)
    The environment we are running in. Used to provide env variable overrides
    from a file in {component-name}/envs/{ENVIRONMENT}

#### Docker

REMOTE_DOCKER_PATH
    Where to push images to.
    eg.
        eu.gcr.io/$GCLOUD_PROJECTID

DOCKER_CMD_AUTHED
    How to execute authenticated docker commands
    eg.
        docker [default]
        ~/google-cloud-sdk/bin/gcloud docker --

#### Github

INTERACT_WITH_GITHUB
    If set, the build will attempt to post commit updates on per-component
    stages, and add component labels if this is for a PR.

PULL_REQUEST_NAMES
    The name of the pull requests this commit is in

BUILD_SHA
    The sha of the built commit

BUILD_URL
    A URL that points to the build job (used in commit status')

GITHUB_AUTH_TOKEN
    Token for accessing github with. Only used if `INTERACT_WITH_GITHUB` is set

GITHUB_PROJECT_USERNAME
    Username to access (eg for https://github.com/example/foo this would be
    `example`)

GITHUB_PROJECT_REPONAME
    Project to access (eg for https://github.com/example/foo this would be
    `foo`)

GITHUB_URL (optional)
    If you use Github Enterprise, set this to your correct Github URL.
    Else, compbuild will default to use github.com.

GIT_TAGGER_EMAIL
    The email address to assign the author of tags to.

## Usage

### Command line interface

    $ compbuild --help
    Intelligent builder for working with component-based repositories

    Usage:
      compbuild discover [--with-versions] [--vs-branch=BRANCH] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild declare [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild build [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild test [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild label <label> [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild tag [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild release [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild get <attr> [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
      compbuild env [<component>...] [--all] [--filter=SELECTOR ...] [--conf=FILE]
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

## Development

$ echo "0.1" > component-builder/VERSION.txt
$ pip install -e component-builder

Now you can play with it!

## Configuring

`builder.ini`, found in the working directory from which you run
`compbuild build` holds configuration for the build process.

Each component that needs building, testing and releasing should be defined
there.
