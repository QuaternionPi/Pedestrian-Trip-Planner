# adapted from https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
class TerminalText:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    DEFAULT = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_color(message: any, color_code: str) -> None:
    print(f"{color_code}{message}{TerminalText.DEFAULT}")


def info(message: any) -> None:
    print_color(f"[INFO] {message}", TerminalText.OKBLUE)


def warning(message: any) -> None:
    print_color(f"[WARN] {message}", TerminalText.WARNING)
