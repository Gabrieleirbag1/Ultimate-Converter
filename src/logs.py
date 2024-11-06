from typing import Optional

class LogColors:
    """Colors for log messages
    
    :param str HEADER: Header color
    :param str OKBLUE: Blue color
    :param str OKCYAN: Cyan color
    :param str OKGREEN: Green color
    :param str WARNING: Warning color
    :param str FAIL: Fail color
    :param str ENDC: End color
    :param str BOLD: Bold color
    :param str UNDERLINE: Underline color"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message: str, level: Optional[str] = "INFO"):
    """Prints log messages with color

    :param str message: The message to print
    :param Optional[str] level: The log level."""
    color = {
        "INFO": LogColors.OKGREEN,
        "WARNING": LogColors.WARNING,
        "ERROR": LogColors.FAIL
    }.get(level, LogColors.ENDC)
    print(f"{color}[{level}] {message}{LogColors.ENDC}")