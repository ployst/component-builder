import datetime
import os
import pytz

import github3


def get_sha():
    return os.environ['BUILD_SHA']


def get_repo():
    gh = github3.login(token=os.environ.get('GITHUB_AUTH_TOKEN'))
    return gh.repository(
        os.environ.get('GITHUB_PROJECT_USERNAME'),
        os.environ.get('GITHUB_PROJECT_REPONAME')
    )


def mark_status_for_component(mode, component_name, status):
    """
    Requires a token that has repo level access.
    """
    sha = get_sha()
    target_url = os.environ['BUILD_URL']
    description = "{0}: {1}".format(mode, component_name)
    repo = get_repo()
    repo.create_status(
        sha=sha,
        state=status,
        description=description,
        target_url=target_url,
        context='builder-{0}-{1}'.format(component_name, mode))


def get_now():
    u = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    return u.isoformat()


def create_tag(tag):
    sha = get_sha()
    date_now = get_now()

    repo = get_repo()
    repo.create_tag(
        tag=tag,
        message='Autotag',
        sha=sha,
        obj_type='commit',
        tagger={
            "name": "Component Builder ",
            "email": os.environ['GIT_TAGGER_EMAIL'],
            "date": date_now
        }
    )


def add_component_label(pr_url, title):
    new_label = 'component:{0}'.format(title)
    issue_id = pr_url.split('/')[-1]
    repo = get_repo()
    issue = repo.issue(issue_id)

    for l in issue.labels():
        if l.name == new_label:
            # Already added to the issue
            return

    issue.add_labels(new_label)
