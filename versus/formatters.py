import datetime
import tempfile
from dataclasses import dataclass, field
from typing import List

import requests
import sh
from versus import conf
from versus.projects import Project


@dataclass
class Formatter:
    name: str
    releases: List["Release"] = field(repr=False, default_factory=list)

    def __init__(self, name: str):
        self.name = name
        self.releases = self.get_releases()

    def format(self, project: Project):
        """
        Take the original code from archive, extract it to a temp directory,
        run the formatter, and then copy the formatter result to the project
        root
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            sh.tar("-C", temp_dir, "-x", "-f", str(project.archive_path))
            self.do_format(temp_dir, project)
            sh.rsync("-a", temp_dir + "/", str(project.root))

    def do_format(self, temp_dir: str, project: Project):
        """
        Run the formatter recursively against the codebase in the project
        """
        raise NotImplementedError()

    def get_releases(self) -> List["Release"]:
        """
        Return a list of releases for the formatter, sorted from oldest to newest
        """
        resp = requests.get(f"https://pypi.org/pypi/{self.name}/json").json()
        ret = []
        for version, data in resp["releases"].items():
            if not data:
                continue
            upload_time = datetime.datetime.strptime(
                data[0]["upload_time"], "%Y-%m-%dT%H:%M:%S"
            )
            ret.append(Release(self, version, upload_time))
        return sorted(ret, key=lambda p: p.upload_time)


class Yapf(Formatter):
    def __init__(self):
        super().__init__("yapf")

    def do_format(self, temp_dir: str, project: Project):
        cmd = sh.Command(conf.PYTHON).bake("-m", "yapf")
        cmd("--in-place", "--recursive", temp_dir, _ok_code=[0, 1, 2])


class Black(Formatter):
    def __init__(self):
        super().__init__("black")

    def do_format(self, temp_dir: str, project: Project):
        cmd = sh.Command(conf.PYTHON).bake("-m", "black")
        cmd(temp_dir, _ok_code=[0, 1, 2, 123])


@dataclass
class Release:
    formatter: Formatter
    version: str
    upload_time: datetime.datetime

    def install(self):
        pip = sh.Command(conf.PYTHON).bake("-m", "pip")
        pip.install(f"{self.formatter.name}=={self.version}")

    @property
    def tag_name(self):
        return f"{self.formatter.name}/{self.version}"


yapf = Yapf()
black = Black()
