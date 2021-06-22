from click.testing import CliRunner
import logging

from hello import hello


def test_hello_world(caplog):
    caplog.set_level(logging.INFO)
    runner = CliRunner()
    result = runner.invoke(hello, ["world"])
    assert result.exit_code == 0
    assert caplog.messages == ["Hello, world!"]
