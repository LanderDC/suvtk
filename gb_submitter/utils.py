import subprocess
import sys


def Exec(CmdLine, fLog=None, capture=False):
    """
    Execute a command line in a shell, logging it to a file if specified.
    If capture is True, suppress printing output to the screen.

    :param CmdLine: The command line to execute
    :type CmdLine: str
    :param fLog: A file object to log the command and results, or None
    :type fLog: file object or None
    :param capture: Whether to capture output instead of printing
    :type capture: bool
    :return: The output of the command if captured, else None
    :rtype: str or None
    """

    def log_or_print(message, is_error=False):
        """Helper to log to file or print to screen, unless capturing."""
        if not capture:  # Only print if capture is False
            if fLog:
                fLog.write(message)
            else:
                output = sys.stderr if is_error else sys.stdout
                output.write(message)

    try:
        # Execute the command
        result = subprocess.run(
            CmdLine,
            shell=True,
            capture_output=capture,
            text=True,
            check=True,
        )

        # Log stdout
        if result.stdout:
            log_or_print(result.stdout)

        # Log stderr
        if result.stderr:
            log_or_print(result.stderr, is_error=True)

        return result.stdout if capture else None  # Return stdout only if capturing

    except subprocess.CalledProcessError as e:
        # Log error details
        if e.stderr:
            log_or_print(e.stderr, is_error=True)
        log_or_print(f"code {e.returncode}\n")
        log_or_print("\n")
        log_or_print(f"{CmdLine}\n")
        log_or_print("\n")
        log_or_print(f"Error code {e.returncode}\n", is_error=True)

        raise  # Re-raise the exception
