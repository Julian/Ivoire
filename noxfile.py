from pathlib import Path

import nox

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
IVOIRE = ROOT / "ivoire"


nox.options.sessions = []


def session(default=True, **kwargs):
    def _session(fn):
        if default:
            nox.options.sessions.append(kwargs.get("name", fn.__name__))
        return nox.session(**kwargs)(fn)

    return _session


@session(python=["3.8", "3.9", "3.10", "3.11", "pypy3"])
def tests(session):
    session.install("virtue", str(ROOT))
    session.run("virtue", "ivoire")
    session.run("ivoire", IVOIRE)


@session()
def audit(session):
    session.install("pip-audit", str(ROOT))
    session.run("python", "-m", "pip_audit")


@session(tags=["build"])
def build(session):
    session.install("build")
    tmpdir = session.create_tmp()
    session.run("python", "-m", "build", str(ROOT), "--outdir", tmpdir)


@session(tags=["style"])
def readme(session):
    session.install("build", "twine")
    tmpdir = session.create_tmp()
    session.run("python", "-m", "build", str(ROOT), "--outdir", tmpdir)
    session.run("python", "-m", "twine", "check", tmpdir + "/*")


@session(tags=["style"])
def style(session):
    session.install(
        "flake8",
        "flake8-broken-line",
        "flake8-bugbear",
        "flake8-commas",
        "flake8-quotes",
        "flake8-tidy-imports",
    )
    session.run(
        "python",
        "-m",
        "flake8",
        str(IVOIRE),
        __file__,
    )


@session()
def typing(session):
    session.install("mypy", str(ROOT))
    session.run("python", "-m", "mypy", str(IVOIRE))
