"""
Core backup management logic.
"""

import os
import shutil
from datetime import datetime


# --- Constants ---

WORKSPACE = "workspace"
SOURCE_DIR = "source_files"
BACKUPS_DIR = "backups"
MOVED_DIR = "moved_files"
LOGS_DIR = "logs"

SAMPLE_FILES = {
    "notes.txt": "# Notes\nUse this file to jot down quick notes.\n",
    "report.txt": "# Report\nAdd your report content here.\n",
    "data.csv": "name,value\nexample,100\n",
    "script.py": '# Sample script\nprint("Hello from Smart Backup Manager!")\n',
}

SUBFOLDERS = [SOURCE_DIR, BACKUPS_DIR, MOVED_DIR, LOGS_DIR]


# --- Helpers ---

def _workspace_path(*parts):
    """Get absolute or relative path within the workspace."""
    return os.path.join(WORKSPACE, *parts)


def _validate_filename(filename):
    """Validate filename for safety (no traversals, empty strings, etc.)."""
    if not filename or not filename.strip():
        return False, "Filename cannot be empty."

    filename = filename.strip()

    # Block path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return False, "Filename must not contain path separators or '..'."

    # Block hidden files and overly long names
    if filename.startswith("."):
        return False, "Hidden files (starting with '.') are not allowed."
    if len(filename) > 255:
        return False, "Filename is too long (max 255 characters)."

    return True, None


def _check_workspace_exists():
    """Ensure the workspace directory exists."""
    if not os.path.exists(WORKSPACE):
        return False, (
            f"'{WORKSPACE}' does not exist. "
            "Please set up the workspace first (option 1)."
        )
    return True, None


def _check_subfolder_exists(subfolder):
    """Ensure a required subfolder exists."""
    path = _workspace_path(subfolder)
    if not os.path.exists(path):
        return False, (
            f"'{subfolder}' folder is missing. "
            "Please set up the workspace first (option 1)."
        )
    return True, None


def _list_files_in(subfolder):
    """List files in subfolder (sorted)."""
    path = _workspace_path(subfolder)
    try:
        return sorted(
            f for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        )
    except OSError:
        return []


def log_operation(action, details=""):
    """Log an action to the daily log file."""
    logspath = _workspace_path(LOGS_DIR)
    if not os.path.isdir(logspath):
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(logspath, f"log_{date_str}.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {action}: {details}\n"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        pass


# --- Core Operations ---

def setup_workspace():
    """Set up the workspace folders and create default sample files."""
    messages = []
    try:
        if not os.path.exists(WORKSPACE):
            os.mkdir(WORKSPACE)
            messages.append(f"Folder '{WORKSPACE}' created.")
        else:
            messages.append(f"Folder '{WORKSPACE}' already exists.")

        for sub in SUBFOLDERS:
            subpath = _workspace_path(sub)
            if not os.path.exists(subpath):
                os.mkdir(subpath)
                messages.append(f"  Subfolder '{sub}' created.")
            else:
                messages.append(f"  Subfolder '{sub}' already exists.")

        source_path = _workspace_path(SOURCE_DIR)
        for fname, content in SAMPLE_FILES.items():
            filepath = os.path.join(source_path, fname)
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                messages.append(f"  File '{fname}' created in '{SOURCE_DIR}'.")
            else:
                messages.append(f"  File '{fname}' already exists in '{SOURCE_DIR}'.")

        log_operation("SETUP", "Workspace initialized")
        return True, "\n".join(messages)

    except OSError as e:
        return False, f"Error setting up workspace: {e}"


def list_source_files():
    """Get list of files in source_files as a formatted string."""
    ok, msg = _check_workspace_exists()
    if not ok:
        return False, msg

    ok, msg = _check_subfolder_exists(SOURCE_DIR)
    if not ok:
        return False, msg

    files = _list_files_in(SOURCE_DIR)
    if not files:
        return True, "No files found in 'source_files'."

    return True, "\n".join(files)


def get_source_files():
    """Get list of source files as a list."""
    ok, _ = _check_workspace_exists()
    if not ok:
        return []
    ok, _ = _check_subfolder_exists(SOURCE_DIR)
    if not ok:
        return []
    return _list_files_in(SOURCE_DIR)


def create_timestamp_backup(filename):
    """Create a timestamped backup copy in the backups folder."""
    ok, msg = _check_workspace_exists()
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(SOURCE_DIR)
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(BACKUPS_DIR)
    if not ok:
        return False, msg

    valid, err = _validate_filename(filename)
    if not valid:
        return False, err

    filename = filename.strip()
    files = _list_files_in(SOURCE_DIR)
    if filename not in files:
        return False, f"'{filename}' does not exist in source_files."

    name, ext = os.path.splitext(filename)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"{name}_{date_str}{ext}"

    destination = _workspace_path(BACKUPS_DIR, backup_name)

    # Avoid name collision
    if os.path.exists(destination):
        micro = datetime.now().strftime("%f")
        backup_name = f"{name}_{date_str}_{micro}{ext}"
        destination = _workspace_path(BACKUPS_DIR, backup_name)

    source = _workspace_path(SOURCE_DIR, filename)
    try:
        shutil.copy2(source, destination)
        log_operation("TIMESTAMP_BACKUP", f"{filename} → {backup_name}")
        return True, f"Backup created: {backup_name}"
    except OSError as e:
        return False, f"Error creating backup: {e}"


def create_quick_copy(filename, overwrite=False):
    """Create a quick copy of a file in the backups folder."""
    ok, msg = _check_workspace_exists()
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(SOURCE_DIR)
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(BACKUPS_DIR)
    if not ok:
        return False, msg

    valid, err = _validate_filename(filename)
    if not valid:
        return False, err

    filename = filename.strip()
    files = _list_files_in(SOURCE_DIR)
    if filename not in files:
        return False, f"'{filename}' does not exist in source_files."

    copy_name = f"copy_{filename}"
    source = _workspace_path(SOURCE_DIR, filename)
    destination = _workspace_path(BACKUPS_DIR, copy_name)

    if os.path.exists(destination) and not overwrite:
        return False, (
            f"'{copy_name}' already exists in backups. "
            "Use the overwrite option to replace it."
        )

    try:
        shutil.copy(source, destination)
        action = "QUICK_COPY_OVERWRITE" if overwrite else "QUICK_COPY"
        log_operation(action, f"{filename} → {copy_name}")
        return True, f"Quick copy created: {copy_name}"
    except OSError as e:
        return False, f"Error creating quick copy: {e}"


def quick_copy_exists(filename):
    """Check if a quick copy of the file exists."""
    copy_name = f"copy_{filename.strip()}"
    return os.path.exists(_workspace_path(BACKUPS_DIR, copy_name))


def move_file(filename):
    """Move a file to moved_files directory."""
    ok, msg = _check_workspace_exists()
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(SOURCE_DIR)
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(MOVED_DIR)
    if not ok:
        return False, msg

    valid, err = _validate_filename(filename)
    if not valid:
        return False, err

    filename = filename.strip()
    files = _list_files_in(SOURCE_DIR)
    if filename not in files:
        return False, f"'{filename}' does not exist in source_files."

    source = _workspace_path(SOURCE_DIR, filename)
    destination = _workspace_path(MOVED_DIR, filename)

    if os.path.exists(destination):
        return False, (
            f"'{filename}' already exists in moved_files. "
            "Cannot overwrite."
        )

    try:
        shutil.move(source, destination)
        log_operation("MOVE", f"{filename} → moved_files/")
        return True, f"File moved: {filename} → moved_files/"
    except OSError as e:
        return False, f"Error moving file: {e}"


def list_backup_files():
    """List all files in the backups directory."""
    ok, msg = _check_workspace_exists()
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(BACKUPS_DIR)
    if not ok:
        return False, msg

    files = _list_files_in(BACKUPS_DIR)
    if not files:
        return True, "No backup files found."

    return True, "\n".join(files)


def get_current_datetime():
    """Get current timestamp."""
    return True, datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_daily_log():
    """Create today's log file if it doesn't exist."""
    ok, msg = _check_workspace_exists()
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(LOGS_DIR)
    if not ok:
        return False, msg

    date_str = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"log_{date_str}.txt"
    log_filepath = _workspace_path(LOGS_DIR, log_filename)

    if os.path.exists(log_filepath):
        return True, f"Today's log file already exists: {log_filename}"

    full_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_filepath, "w", encoding="utf-8") as f:
            f.write(f"Smart Backup Manager -- Log created on {full_time}\n")
            f.write("=" * 50 + "\n\n")
        log_operation("LOG_CREATE", f"Created {log_filename}")
        return True, f"Log file created: {log_filename}"
    except OSError as e:
        return False, f"Error creating log file: {e}"


def get_backup_paths():
    """Get absolute paths of all backup files."""
    ok, msg = _check_workspace_exists()
    if not ok:
        return False, msg
    ok, msg = _check_subfolder_exists(BACKUPS_DIR)
    if not ok:
        return False, msg

    backuppath = _workspace_path(BACKUPS_DIR)
    try:
        files = []
        for item in sorted(os.listdir(backuppath)):
            itempath = os.path.join(backuppath, item)
            if os.path.isfile(itempath):
                files.append(os.path.abspath(itempath))

        if not files:
            return True, "No backup files found."

        return True, "\n".join(files)
    except OSError as e:
        return False, f"Error reading backup paths: {e}"
