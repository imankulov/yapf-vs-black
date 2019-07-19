import compileall
import datetime
from dataclasses import dataclass, field

import sh
import yaml
from versus.formatters import Formatter, Release
from versus.projects import Project


@dataclass
class GitStats:
    lines_added: int = field(default=0)
    lines_deleted: int = field(default=0)


def is_valid(project: Project) -> bool:
    """
    Return true if all the code inside the project directory is valid
    """
    return bool(compileall.compile_dir(project.root, quiet=1))


def lines_of_code(project: Project) -> int:
    """
    Return the number of lines of code, calculated with cloc
    """
    ret = sh.cloc("--quiet", "--include-lang=Python", "--yaml", str(project.root))
    ret_obj = list(yaml.safe_load_all(str(ret)))
    return ret_obj[0]["Python"]["code"]


def git_has_object(project: Project, name: str) -> bool:
    """
    Return True if branch branch_name exists for the project
    """
    ret = project.git("rev-parse", "--verify", name, _ok_code=[0, 128])
    return ret.exit_code == 0


def git_stats_release(project: Project, release: Release) -> GitStats:
    """
    Return total number of insertions and deletions for the project
    """
    return _git_stats(project, f"{release.tag_name}~1", release.tag_name)


def git_stats_date_range(
    project: Project,
    formatter: Formatter,
    date_start: datetime.datetime,
    date_end: datetime.datetime,
) -> GitStats:
    """
    Return total number of insertions and deletions for formatter for the given
    date range (from start to end)
    """
    name_start = f"{formatter.name}@{{{date_start:%F %T}}}"
    name_end = f"{formatter.name}@{{{date_end:%F %T}}}"
    return _git_stats(project, name_start, name_end)


def _git_stats(project: Project, name_start: str, name_end: str) -> GitStats:
    stats = GitStats()
    diff_version = f"{name_start}..{name_end}"
    ret = str(project.git("diff", "--numstat", diff_version, _tty_out=False))
    for line in ret.splitlines():
        chunks = line.split()
        stats.lines_added += int(chunks[0])
        stats.lines_deleted += int(chunks[1])
    return stats
