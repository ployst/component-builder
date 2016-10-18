# Set by the component builder
DOCKER_IMAGE
    This is the name of the service
DOCKER_TAG
    TODO: change this. We should query the service for what it wants RELEASE_TAG
    to be
    Set to `RELEASE_TAG`
REPORT_LOCATION
    Set to CENTRAL_REPORT_LOCATION/${component-name}

# Set by the caller (in Jenkinsfile or circle.yml)
REMOTE_DOCKER_PATH
    Where to push images to.
    eg.
        eu.gcr.io/$GCLOUD_PROJECTID
DOCKER_PUSH_COMMAND
    How to perform the docker push.
    eg.
        docker push
        ~/google-cloud-sdk/bin/gcloud docker push

RELEASE_TAG
    TODO: Change this. We should query each service for what it wants RELEASE_TAG
    to be.

INTERACT_WITH_GITHUB
    If set, the build will attempt to post commit updates on per-component
    stages, and add component labels if this is for a PR.

PULL_REQUEST_NAMES
    The name of the pull requests this commit is in

BUILD_SHA
    The sha of the built commit

BUILD_BRANCH
    The currently built branch

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

CENTRAL_REPORT_LOCATION
    A local directory that per component reports should be written to.

ENVIRONMENT (local|CI|etc..)
    The environment we are running in. Used to provide env variable overrides
    from a file in {component-name}/envs/{ENVIRONMENT}
