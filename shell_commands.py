"""Shell commands used by application."""

from subprocess import PIPE, Popen, TimeoutExpired
from typing import List, NamedTuple

from exceptions import CommandExecutionFailed, CommandRunsTooLong, NoSuchCommand


class CommandExecutionResult(NamedTuple):
    """Result of shell command execution."""

    stdout_data: str
    stderr_data: bytes
    exit_code: int


class ShellCommand:
    """
    Unix shell command.

    Application works like request -> response and
    it's runtime must be as fast as it possible.
    That's why there is a timeout field in this class.
    """

    def __init__(self, executable: str, arguments: List[str] = [], timeout: float = 5):
        """Shell command constructor."""
        self.executable = executable
        self.arguments = arguments
        self.timeout = timeout

    def execute(self) -> CommandExecutionResult:
        """Execute shell command."""
        try:
            process = Popen(args=[self.executable, *self.arguments], stdout=PIPE)
        except FileNotFoundError:
            raise NoSuchCommand(
                f"There's no command '{self.executable}' in your system"
            )
        try:
            (stdout, stderr) = process.communicate(timeout=self.timeout)
            exit_code = process.wait(timeout=self.timeout)
        except TimeoutExpired as err:
            process.kill
            raise CommandRunsTooLong(
                f"Command '{err.cmd}' runs more than {err.timeout} seconds"
            )
        if stderr is not None or exit_code != 0:
            raise CommandExecutionFailed(
                f"Command has ended with exit_code: "
                f"{exit_code} and stderr:\n{stderr}"  # type: ignore
            )
        return CommandExecutionResult(
            stdout_data=self._preprocess_stdout_data(stdout),
            stderr_data=stderr,
            exit_code=exit_code,
        )

    def _preprocess_stdout_data(self, stdout_data: bytes) -> str:
        """Decode, strip, lower stdout data."""
        return stdout_data.decode().strip().lower()
