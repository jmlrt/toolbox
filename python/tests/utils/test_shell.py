import os

import pytest

from utils.shell import (
    VariableNotFoundError,
    check_command_in_path,
    check_environment_variable,
)


def test_check_command_in_path():
    assert "/bin/cat" in check_command_in_path("cat")
    with pytest.raises(FileNotFoundError):
        assert check_command_in_path("fake-command")


def test_check_environment_variable():
    os.environ["TEST_VARIABLE"] = "foo"
    assert check_environment_variable("TEST_VARIABLE") == "foo"
    with pytest.raises(VariableNotFoundError):
        assert check_environment_variable("FAKE_VARIABLE")
