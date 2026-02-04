"""
Terminal color formatting utilities.

This module provides functions for formatting terminal output with colors
and styles.
"""

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PURPLE = '\033[38;5;129m'
    PINK = '\033[38;5;205m'
    LIGHT_GREY = '\033[37m'
    DARK_GREY = '\033[90m'


def bold(text: str) -> str:
    """Format text as bold."""
    return f"{Colors.BOLD}{text}{Colors.ENDC}"


def green(text: str) -> str:
    """Format text in green color."""
    return f"{Colors.GREEN}{text}{Colors.ENDC}"


def red(text: str) -> str:
    """Format text in red color."""
    return f"{Colors.RED}{text}{Colors.ENDC}"


def cyan(text: str) -> str:
    """Format text in cyan color."""
    return f"{Colors.CYAN}{text}{Colors.ENDC}"


def yellow(text: str) -> str:
    """Format text in yellow color."""
    return f"{Colors.YELLOW}{text}{Colors.ENDC}"


def purple(text: str) -> str:
    """Format text in purple color."""
    return f"{Colors.PURPLE}{text}{Colors.ENDC}"


def pink(text: str) -> str:
    """Format text in pink color."""
    return f"{Colors.PINK}{text}{Colors.ENDC}"


def light_grey(text: str) -> str:
    """Format text in light grey color."""
    return f"{Colors.LIGHT_GREY}{text}{Colors.ENDC}"


def dark_grey(text: str) -> str:
    """Format text in dark grey color."""
    return f"{Colors.DARK_GREY}{text}{Colors.ENDC}"


def blue(text: str) -> str:
    """Format text in blue color."""
    return f"{Colors.BLUE}{text}{Colors.ENDC}"


def underline(text: str) -> str:
    """Format text with underline."""
    return f"{Colors.UNDERLINE}{text}{Colors.ENDC}"


def header(text: str) -> str:
    """Format text as a header."""
    return f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}"
