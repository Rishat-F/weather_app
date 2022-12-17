"""End to end tests."""

import re
import sys
from subprocess import PIPE, Popen
from typing import NamedTuple

SUCCESS_EXIT_CODE = 0


class CommandExecutionResult(NamedTuple):
    """Result of shell command execution."""

    stdout_data: str
    stderr_data: bytes
    exit_code: int


class WeatherCommand:
    """Shell command for run application."""

    PYTHON_EXECUTABLE = sys.executable
    ENTRY_POINT = ["weather.py"]

    def execute(self) -> CommandExecutionResult:
        """Execute shell command."""
        process = Popen(args=[self.PYTHON_EXECUTABLE, *self.ENTRY_POINT], stdout=PIPE)
        (stdout, stderr) = process.communicate()
        exit_code = process.wait()
        return CommandExecutionResult(
            stdout_data=self._preprocess_stdout_data(stdout),
            stderr_data=stderr,
            exit_code=exit_code,
        )

    def _preprocess_stdout_data(self, stdout_data: bytes) -> str:
        """Decode, strip, lower stdout data."""
        return stdout_data.decode().strip()


class TestE2E(WeatherCommand):
    """End to end test."""

    def test_e2e(self) -> None:
        """Check if application really work."""
        expected_weather_output_pattern = (
            r"[\w -]+, [-+]?\d{1,3}(?:°C|°K|°F), [\w ]+\n\n"
            r"[\w ]+\n"
            r"\w+: \d+(?:\.\d\d?)?(?:m/s|km/h|mph)\n"
            r"\w+: \d\d:\d\d\n"
            r"\w+: \d\d:\d\d"
        )
        stdout, stderr, exit_code = self.execute()
        assert re.fullmatch(expected_weather_output_pattern, stdout)
        assert stderr is None
        assert exit_code == SUCCESS_EXIT_CODE
