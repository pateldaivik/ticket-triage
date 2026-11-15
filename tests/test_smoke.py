from typer.testing import CliRunner

from ticket_triage.cli import app


def test_cli_help():
    assert CliRunner().invoke(app, ["--help"]).exit_code == 0
