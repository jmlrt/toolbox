from click.testing import CliRunner

from hello import hello


def test_hello_world():
    runner = CliRunner()
    import pytest

    pytest.set_trace()
    result = runner.invoke(hello, ["world"], catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == "Hello, world!\n"
