"""
Command Line Interface for Smart Backup Manager.
"""

import sys
import backup_core


# --- Helpers ---

def _print_result(success, message):
    """Print result with status symbol."""
    prefix = "✓" if success else "✗"
    print(f"\n  {prefix} {message}")


def _get_filename_from_user(available_files, action_label="select"):
    """Let user select a file from the list."""
    if not available_files:
        print("\n  No files available.")
        return None

    print(f"\n  Available files ({len(available_files)}):")
    for i, name in enumerate(available_files, 1):
        print(f"    {i}. {name}")

    while True:
        choice = input(f"\n  Enter file name or # to {action_label} (or 'q' to cancel): ").strip()
        if choice.lower() == "q":
            print("  Operation cancelled.")
            return None

        # Allow selection by number
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(available_files):
                return available_files[idx]
            print(f"  Invalid number. Choose 1–{len(available_files)}.")
            continue

        # Allow selection by name
        if choice in available_files:
            return choice

        print(f"  '{choice}' not found. Try again.")


def _confirm(prompt):
    """Prompt user for confirmation."""
    while True:
        answer = input(f"  {prompt} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please enter 'y' or 'n'.")


# --- Menu actions ---

def do_setup():
    success, msg = backup_core.setup_workspace()
    _print_result(success, msg)


def do_show_source_files():
    success, msg = backup_core.list_source_files()
    _print_result(success, msg)


def do_timestamp_backup():
    files = backup_core.get_source_files()
    filename = _get_filename_from_user(files, "backup")
    if filename is None:
        return
    success, msg = backup_core.create_timestamp_backup(filename)
    _print_result(success, msg)


def do_quick_copy():
    files = backup_core.get_source_files()
    filename = _get_filename_from_user(files, "copy")
    if filename is None:
        return
    # Offer overwrite if copy exists
    overwrite = False
    if backup_core.quick_copy_exists(filename):
        print(f"\n  A quick copy of '{filename}' already exists.")
        overwrite = _confirm("Overwrite it?")
        if not overwrite:
            print("  Operation cancelled.")
            return
    success, msg = backup_core.create_quick_copy(filename, overwrite=overwrite)
    _print_result(success, msg)


def do_move_file():
    files = backup_core.get_source_files()
    filename = _get_filename_from_user(files, "move")
    if filename is None:
        return
    # Destructive move confirmation
    if not _confirm(f"Move '{filename}' to moved_files? This removes it from source_files."):
        print("  Operation cancelled.")
        return
    success, msg = backup_core.move_file(filename)
    _print_result(success, msg)


def do_show_backup_files():
    success, msg = backup_core.list_backup_files()
    _print_result(success, msg)


def do_show_datetime():
    success, msg = backup_core.get_current_datetime()
    _print_result(success, f"Current Date & Time: {msg}")


def do_create_log():
    success, msg = backup_core.create_daily_log()
    _print_result(success, msg)


def do_show_backup_paths():
    success, msg = backup_core.get_backup_paths()
    _print_result(success, msg)


# --- Main menu ---

MENU = """
  ╔══════════════════════════════════════════════╗
  ║       Smart Backup Manager — CLI Mode        ║
  ╠══════════════════════════════════════════════╣
  ║  1.  Setup Workspace                         ║
  ║  2.  Show Source Files                        ║
  ║  3.  Create Timestamp Backup (copy2)          ║
  ║  4.  Create Quick Copy                        ║
  ║  5.  Move File to moved_files                 ║
  ║  6.  Show Backup Files                        ║
  ║  7.  Show Current Date & Time                 ║
  ║  8.  Create Daily Log File                    ║
  ║  9.  Show Full Paths of Backup Files          ║
  ║ 10.  Exit                                     ║
  ╚══════════════════════════════════════════════╝
"""

ACTIONS = {
    1: do_setup,
    2: do_show_source_files,
    3: do_timestamp_backup,
    4: do_quick_copy,
    5: do_move_file,
    6: do_show_backup_files,
    7: do_show_datetime,
    8: do_create_log,
    9: do_show_backup_paths,
}


def main():
    """CLI entry point and menu loop."""
    print("\n  Welcome to Smart Backup Manager!")
    print("  ─────────────────────────────────")

    while True:
        print(MENU)
        choice_str = input("  Enter your choice (1–10): ").strip()

        if not choice_str:
            print("\n  ✗ Please enter a number between 1 and 10.")
            continue

        if not choice_str.isdigit():
            print(f"\n  ✗ '{choice_str}' is not a valid number. Please enter 1–10.")
            continue

        choice = int(choice_str)

        if choice == 10:
            print("\n  Goodbye! 👋")
            break

        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print(f"\n  ✗ '{choice}' is not a valid option. Please enter 1–10.")


if __name__ == "__main__":
    main()
