"""
Smart Backup Manager entry point.

Usage:
    python main.py          Launch GUI (default)
    python main.py --cli    Launch CLI mode
"""

import sys


def main():
    if "--cli" in sys.argv:
        import cli
        cli.main()
    else:
        import gui
        gui.main()


if __name__ == "__main__":
    main()
