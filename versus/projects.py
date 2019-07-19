import pathlib
from dataclasses import dataclass

import sh
from versus import conf


@dataclass
class Project:
    """
    Class for a project to test. Project can be "django", "flask", etc.
    """

    name: str
    url: str
    default_branch: str = "master"

    @property
    def root(self):
        return conf.PROJECTS_ROOT / self.name

    @property
    def archive_path(self):
        return pathlib.Path(str(self.root) + ".tar")

    @property
    def git(self):
        return sh.git.bake(_cwd=self.root)

    def clone(self):
        """
        Clone project from remote git repository
        """
        if not self.root.is_dir():
            sh.git.clone(self.url, self.name, _cwd=conf.PROJECTS_ROOT)

    def make_archive(self):
        """
        Make archive of the
        """
        self.git.archive(
            self.default_branch, format="tar", output=str(self.archive_path)
        )


# Two projects for testing

# about 800 LOC
dotenv = Project("dotenv", "git@github.com:theskumar/python-dotenv.git", "master")

# Almost 10k LOC
flask = Project("flask", "git@github.com:pallets/flask.git", "master")
