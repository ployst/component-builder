import datetime
import os

import github3
import pytz


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


def update_branch(branch_name):
    sha = get_sha()
    repo = get_repo()

    b = repo.ref('heads/{0}'.format(branch_name))
    if b and not isinstance(b, github3.exceptions.UnprocessableResponseBody):
        b.update(sha, force=True)
    else:
        repo.create_ref('refs/heads/{0}'.format(branch_name), sha)


def validate_pr_url(pr_url):
    issue_id = pr_url.split('/')[-1]
    try:
        int(issue_id)
        return True
    except ValueError:
        raise ValidationError(
            'URL "{0}" not in the correct format'
            ' <string>/<id:int>'.format(pr_url)
        )


def replace_labels(component_titles, current_labels):
    new_component_labels = {
        'component:{0}'.format(title) for title in component_titles}
    current_component_labels = {
        l.name for l in current_labels if l.name.startswith('component:')}

    to_add = new_component_labels.difference(current_component_labels)
    to_del = current_component_labels.difference(new_component_labels)
    return (to_add, to_del)


def add_pr_components_labels(pr_url, titles):
    validate_pr_url(pr_url)
    issue_id = pr_url.split('/')[-1]
    repo = get_repo()
    issue = repo.issue(issue_id)

    to_add, to_del = replace_labels(titles, issue.labels())
    for label in to_del:
        issue.remove_label(label)
    issue.add_labels(*to_add)


class ValidationError(Exception):
    pass
