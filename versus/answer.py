import datetime

import pandas as pd
from versus import git_stats_release
from versus.formatters import Formatter
from versus.projects import Project
from versus.utils import git_stats_date_range, lines_of_code


def ultimate_answer_by_date(
    project: Project,
    formatter: Formatter,
    days: int,
    date_start: datetime.datetime = None,
) -> pd.DataFrame:
    """
    Gives the ultimate answer to the question what would happen if I use
    "formatter" for the "project" and updated that formatter every "days"
    """

    now = datetime.datetime.utcnow()

    date = []
    lines_added = []
    lines_deleted = []

    if date_start is None:
        date_start = formatter.releases[0].upload_time
    while True:
        date_end = date_start + datetime.timedelta(days)
        if date_end > now:
            break
        stats = git_stats_date_range(project, formatter, date_start, date_end)
        date.append(date_end)
        lines_added.append(stats.lines_added)
        lines_deleted.append(stats.lines_deleted)
        date_start = date_end

    lines_total = [lines_of_code(project)] * len(lines_added)
    df = pd.DataFrame(
        dict(
            date=date[1:],
            lines_added=lines_added[1:],
            lines_deleted=lines_deleted[1:],
            lines_total=lines_total[1:],
        )
    )
    df["affected_pct"] = (df.lines_added + df.lines_deleted) * 100 / df.lines_total
    return df


def ultimate_answer_by_version(project: Project, formatter: Formatter) -> pd.DataFrame:
    """
    Gives the ultimate answer to the question what would happen if I use
    "formatter" for the "project" and updated that formatter every time a new
    version comes out
    """
    version = []
    date = []
    lines_added = []
    lines_deleted = []

    for release in formatter.releases:
        stats = git_stats_release(project, release)
        version.append(release.version)
        date.append(release.upload_time)
        lines_added.append(stats.lines_added)
        lines_deleted.append(stats.lines_deleted)

    lines_total = [lines_of_code(project)] * len(lines_added)
    df = pd.DataFrame(
        dict(
            version=version[1:],
            date=date[1:],
            lines_added=lines_added[1:],
            lines_deleted=lines_deleted[1:],
            lines_total=lines_total[1:],
        )
    )
    df["affected_pct"] = (df.lines_added + df.lines_deleted) * 100 / df.lines_total
    return df
