import os

from versus.formatters import Formatter, Release
from versus.projects import Project
from versus.utils import git_has_object


def run_tests(project: Project, formatter: Formatter, reset=True):
    if reset:
        project.git.reset("--hard", "HEAD")
        project.git.checkout(project.default_branch)
        if git_has_object(project, formatter.name):
            project.git.branch("-D", formatter.name)
        project.git.checkout("-b", formatter.name)

    for release in formatter.releases:
        run_test(project, release)


def run_test(project: Project, release: Release):
    """
    Run one iteration of the formatter with the release "release" for
    the project "project", see if the result is broken,
    and commit the results to the repository.
    """
    print(f"Run test for {release.tag_name}")
    if git_has_object(project, release.tag_name):
        project.git.tag("-d", release.tag_name)

    release.install()
    project.git.reset("--hard", "HEAD")
    release.formatter.format(project)
    commit_message = (
        f"{release.formatter.name}/{release.version} "
        f"from {release.upload_time:%F %T}"
    )
    dt = release.upload_time.strftime("%F %T")
    project.git.commit(
        "--date",
        dt,
        "--allow-empty",
        "--all",
        "--message",
        commit_message,
        _env=dict(os.environ, GIT_COMMITTER_DATE=dt),
    )
    project.git.tag(release.tag_name)
