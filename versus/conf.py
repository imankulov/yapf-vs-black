import pathlib

# This project root
ROOT = pathlib.Path(__file__).parent.parent.absolute()

# Projects root
PROJECTS_ROOT = ROOT / "projects"

# Virtualenv root
VENV_ROOT = ROOT / "env"

# Path to Python interpreter
PYTHON = VENV_ROOT / "bin" / "python"
