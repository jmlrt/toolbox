import os
import shutil


class VariableNotFoundError(Exception):
    pass


def check_command_in_path(command, error_message=None):
    command_path = shutil.which(command)
    if command_path is None:
        raise FileNotFoundError(f"{command} missing\n{error_message}")
    return command_path


def check_environment_variable(var, error_message=None):
    try:
        value = os.environ[var]
    except KeyError:
        raise VariableNotFoundError(
            f"{var} environment variable missing\n{error_message}"
        )
    return value
