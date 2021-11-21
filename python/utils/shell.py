import os
import subprocess


class VariableNotFoundError(Exception):
    pass


def check_command_in_path(command, error_message=None):
    command_run = subprocess.run(
        ["command", "-v", command], capture_output=True, text=True
    )
    if command_run.returncode != 0:
        raise FileNotFoundError(f"{command} missing\n{error_message}")
    return command_run.stdout


def check_environment_variable(var, error_message=None):
    try:
        value = os.environ[var]
    except KeyError:
        raise VariableNotFoundError(
            f"{var} environment variable missing\n{error_message}"
        )
    return value
