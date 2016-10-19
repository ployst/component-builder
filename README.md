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

## Typical Flow

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
    # TODO: this doesn't actually happen yet
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

DOCKER_PUSH_COMMAND
    How to perform the docker push.
    eg.
        docker push
        ~/google-cloud-sdk/bin/gcloud docker push

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

GIT_TAGGER_EMAIL
    The email address to assign the author of tags to.

## Usage

### Command line interface

    $ compbuild --help
    Intelligent builder for working with component-based repositories

    Usage:
      compbuild discover [--all]
      compbuild build [<component>...] [--all]
      compbuild env [<component>...] [--all]
      compbuild release [<component>...] [--all]
      compbuild test [<component>...] [--all]
      compbuild tag [<component>...] [--all]
      compbuild label <label> [<component>...] [--all]
      compbuild -h | --help
      compbuild --version

    Options:
      -h --help            Show this screen.
      --all                Do all the components
      --version            Show version.

## Development

$ pip install -e builder

Now you can play with it!

## Configuring

`builder.ini`, found in the working directory from which you run
`compbuild build` holds configuration for the build process.

Each component that needs building, testing and releasing should be defined
there.
