# Smart Backup Manager

A Python-based file backup and workspace management tool with both **CLI** and **GUI** interfaces.

## Features

- 🏗️ **Workspace Setup** — Automatically create a structured workspace with source files, backups, moved files, and logs directories
- ⏱️ **Timestamp Backups** — Create timestamped copies of source files with collision avoidance
- 📋 **Quick Copy** — One-click file duplication with optional overwrite
- 📦 **File Moving** — Move files between directories with confirmation prompts
- 📝 **Daily Logging** — Automatic daily log files with operation tracking
- 📍 **Path Display** — View full absolute paths of all backup files
- 🎨 **Dual Interface** — Modern dark-themed GUI + full-featured CLI

## Installation

**Requirements:** Python 3.7+ (no external dependencies — uses only the standard library)
[text](../month1/automation/smart_backup_manager.py)
```bash
git clone https://github.com/YOUR_USERNAME/smart_backup_manager.git
cd smart_backup_manager
```

## Usage

### GUI Mode (Default)

```bash
python main.py
```

### CLI Mode

```bash
python main.py --cli
```

## Project Structure

```
smart_backup_manager/
├── main.py           # Entry point (--cli flag for CLI mode)
├── backup_core.py    # All business logic (no I/O)
├── cli.py            # CLI interface
├── gui.py            # Tkinter GUI interface
├── requirements.txt  # Dependencies (stdlib only for now)
├── LICENSE           # MIT License
├── README.md         # This file
└── workspace/        # Runtime directory (auto-created, gitignored)
    ├── source_files/ # Your source files
    ├── backups/      # Timestamped backups and quick copies
    ├── moved_files/  # Files moved from source
    └── logs/         # Daily operation logs
```

## How It Works

1. **Setup Workspace** — Creates the directory structure and sample files
2. **Choose an action** — Select from 9 operations via GUI buttons or CLI menu
3. **All operations are logged** — Every action is recorded in the daily log file

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
