"""
Tkinter-based GUI for Smart Backup Manager.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
from datetime import datetime
import backup_core


# --- Color Palette ---

COLORS = {
    "bg_dark": "#1a1b2e",
    "bg_sidebar": "#16172b",
    "bg_panel": "#1e2040",
    "bg_input": "#282a4a",
    "accent": "#7c6fff",
    "accent_hover": "#9b8aff",
    "accent_success": "#4ade80",
    "accent_error": "#f87171",
    "accent_warning": "#fbbf24",
    "text_primary": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "border": "#2d2f52",
    "button_bg": "#2d2f52",
    "button_hover": "#3b3d66",
}


# --- Application ---

class SmartBackupApp:
    """GUI application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Backup Manager")
        self.root.geometry("900x600")
        self.root.minsize(750, 500)
        self.root.configure(bg=COLORS["bg_dark"])

        # Try setting window icon
        try:
            self.root.iconbitmap(default="")
        except tk.TclError:
            pass

        self._setup_fonts()
        self._setup_styles()
        self._build_ui()

        # Center window
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    # --- Fonts & Styles ---

    def _setup_fonts(self):
        self.font_title = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_heading = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.font_body = tkfont.Font(family="Consolas", size=10)
        self.font_button = tkfont.Font(family="Segoe UI", size=10)
        self.font_status = tkfont.Font(family="Segoe UI", size=9)

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Scrollbar styling
        self.style.configure(
            "Custom.Vertical.TScrollbar",
            background=COLORS["bg_panel"],
            troughcolor=COLORS["bg_dark"],
            arrowcolor=COLORS["text_secondary"],
        )

    # --- UI Construction ---

    def _build_ui(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_content_area()
        self._build_status_bar()

    def _build_sidebar(self):
        sidebar = tk.Frame(
            self.main_frame,
            bg=COLORS["bg_sidebar"],
            width=250,
            padx=12,
            pady=12,
        )
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Sidebar header/title
        title_frame = tk.Frame(sidebar, bg=COLORS["bg_sidebar"])
        title_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            title_frame,
            text="💾",
            font=tkfont.Font(size=24),
            bg=COLORS["bg_sidebar"],
            fg=COLORS["accent"],
        ).pack()

        tk.Label(
            title_frame,
            text="Smart Backup\nManager",
            font=self.font_title,
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_primary"],
            justify=tk.CENTER,
        ).pack(pady=(4, 0))

        # Divider line
        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill=tk.X, pady=(0, 16))

        # Menu buttons
        buttons = [
            ("🏗️  Setup Workspace", self._on_setup),
            ("📂  Source Files", self._on_show_source),
            ("⏱️  Timestamp Backup", self._on_timestamp_backup),
            ("📋  Quick Copy", self._on_quick_copy),
            ("📦  Move File", self._on_move_file),
            ("🗄️  Backup Files", self._on_show_backups),
            ("🕐  Date & Time", self._on_datetime),
            ("📝  Create Log", self._on_create_log),
            ("📍  Backup Paths", self._on_backup_paths),
        ]

        for text, command in buttons:
            btn = tk.Button(
                sidebar,
                text=text,
                font=self.font_button,
                bg=COLORS["button_bg"],
                fg=COLORS["text_primary"],
                activebackground=COLORS["button_hover"],
                activeforeground=COLORS["text_primary"],
                relief=tk.FLAT,
                anchor=tk.W,
                padx=12,
                pady=8,
                cursor="hand2",
                command=command,
            )
            btn.pack(fill=tk.X, pady=2)

            # Mouse hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLORS["button_hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=COLORS["button_bg"]))

        # Push bottom button down
        tk.Frame(sidebar, bg=COLORS["bg_sidebar"]).pack(fill=tk.BOTH, expand=True)

        # Reset log area
        clear_btn = tk.Button(
            sidebar,
            text="🧹  Clear Output",
            font=self.font_button,
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_hover"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self._clear_output,
        )
        clear_btn.pack(fill=tk.X, pady=(8, 0))
        clear_btn.bind("<Enter>", lambda e: clear_btn.configure(bg=COLORS["accent_hover"]))
        clear_btn.bind("<Leave>", lambda e: clear_btn.configure(bg=COLORS["accent"]))

    def _build_content_area(self):
        content = tk.Frame(self.main_frame, bg=COLORS["bg_dark"], padx=16, pady=16)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Log section header
        header = tk.Frame(content, bg=COLORS["bg_dark"])
        header.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            header,
            text="Output",
            font=self.font_heading,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(side=tk.LEFT)

        self.timestamp_label = tk.Label(
            header,
            text="",
            font=self.font_status,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_muted"],
        )
        self.timestamp_label.pack(side=tk.RIGHT)

        # Scrollable console log area
        output_frame = tk.Frame(content, bg=COLORS["bg_panel"])
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(
            output_frame,
            font=self.font_body,
            bg=COLORS["bg_panel"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            selectforeground="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=12,
            wrap=tk.WORD,
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )

        scrollbar = ttk.Scrollbar(
            output_frame,
            orient=tk.VERTICAL,
            command=self.output_text.yview,
            style="Custom.Vertical.TScrollbar",
        )
        self.output_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Custom text tag colors
        self.output_text.tag_configure("success", foreground=COLORS["accent_success"])
        self.output_text.tag_configure("error", foreground=COLORS["accent_error"])
        self.output_text.tag_configure("info", foreground=COLORS["accent"])
        self.output_text.tag_configure("warning", foreground=COLORS["accent_warning"])
        self.output_text.tag_configure("header", foreground=COLORS["text_primary"], font=self.font_heading)

    def _build_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="  Ready",
            font=self.font_status,
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
            padx=12,
            pady=6,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Output helpers ---

    def _append_output(self, text, tag=None):
        """Write message to console log."""
        self.output_text.configure(state=tk.NORMAL)
        if tag:
            self.output_text.insert(tk.END, text + "\n", tag)
        else:
            self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)

        # Update last run timestamp
        now = datetime.now().strftime("%H:%M:%S")
        self.timestamp_label.configure(text=f"Last update: {now}")

    def _show_result(self, success, message, operation="Operation"):
        """Show operation status."""
        self._append_output(f"─── {operation} ───", "header")
        tag = "success" if success else "error"
        prefix = "✓" if success else "✗"
        self._append_output(f"  {prefix} {message}", tag)
        self._append_output("")  # blank line

        # Update footer text
        status_text = f"  ✓ {operation} completed" if success else f"  ✗ {operation} failed"
        status_color = COLORS["accent_success"] if success else COLORS["accent_error"]
        self.status_bar.configure(text=status_text, fg=status_color)

    def _clear_output(self):
        """Clear console logs."""
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.DISABLED)
        self.status_bar.configure(text="  Ready", fg=COLORS["text_secondary"])
        self.timestamp_label.configure(text="")

    def _ask_filename(self, title, action_label="select"):
        """Show file selection dialog."""
        files = backup_core.get_source_files()
        if not files:
            messagebox.showinfo("No Files", "No files found in source_files.")
            return None

        # Select file window
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("350x400")
        dialog.configure(bg=COLORS["bg_dark"])
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 200
        dialog.geometry(f"+{x}+{y}")

        selected = [None]

        tk.Label(
            dialog,
            text=f"Select a file to {action_label}:",
            font=self.font_heading,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
        ).pack(pady=(16, 8), padx=16, anchor=tk.W)

        # Scrollable list of files
        listbox_frame = tk.Frame(dialog, bg=COLORS["bg_dark"])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        listbox = tk.Listbox(
            listbox_frame,
            font=self.font_body,
            bg=COLORS["bg_panel"],
            fg=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            activestyle="none",
        )
        listbox.pack(fill=tk.BOTH, expand=True)

        for f in files:
            listbox.insert(tk.END, f"  {f}")

        def on_select():
            sel = listbox.curselection()
            if sel:
                selected[0] = files[sel[0]]
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Window buttons
        btn_frame = tk.Frame(dialog, bg=COLORS["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=16, pady=(0, 16))

        tk.Button(
            btn_frame,
            text=f"  {action_label.capitalize()}  ",
            font=self.font_button,
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_hover"],
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=on_select,
        ).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(
            btn_frame,
            text="  Cancel  ",
            font=self.font_button,
            bg=COLORS["button_bg"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["button_hover"],
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=on_cancel,
        ).pack(side=tk.RIGHT)

        # Bind double-click handler
        listbox.bind("<Double-Button-1>", lambda e: on_select())

        dialog.wait_window()
        return selected[0]

    # --- Action handlers ---

    def _on_setup(self):
        success, msg = backup_core.setup_workspace()
        self._show_result(success, msg, "Setup Workspace")

    def _on_show_source(self):
        success, msg = backup_core.list_source_files()
        self._show_result(success, msg, "Source Files")

    def _on_timestamp_backup(self):
        filename = self._ask_filename("Timestamp Backup", "backup")
        if filename is None:
            return
        success, msg = backup_core.create_timestamp_backup(filename)
        self._show_result(success, msg, "Timestamp Backup")

    def _on_quick_copy(self):
        filename = self._ask_filename("Quick Copy", "copy")
        if filename is None:
            return
        overwrite = False
        if backup_core.quick_copy_exists(filename):
            overwrite = messagebox.askyesno(
                "Copy Exists",
                f"A quick copy of '{filename}' already exists.\n\nOverwrite it?",
            )
            if not overwrite:
                self.status_bar.configure(
                    text="  Quick Copy cancelled", fg=COLORS["accent_warning"]
                )
                return
        success, msg = backup_core.create_quick_copy(filename, overwrite=overwrite)
        self._show_result(success, msg, "Quick Copy")

    def _on_move_file(self):
        filename = self._ask_filename("Move File", "move")
        if filename is None:
            return
        confirm = messagebox.askyesno(
            "Confirm Move",
            f"Move '{filename}' to moved_files?\n\n"
            "This will remove it from source_files.",
        )
        if not confirm:
            self.status_bar.configure(
                text="  Move cancelled", fg=COLORS["accent_warning"]
            )
            return
        success, msg = backup_core.move_file(filename)
        self._show_result(success, msg, "Move File")

    def _on_show_backups(self):
        success, msg = backup_core.list_backup_files()
        self._show_result(success, msg, "Backup Files")

    def _on_datetime(self):
        success, msg = backup_core.get_current_datetime()
        self._show_result(success, f"Current Date & Time: {msg}", "Date & Time")

    def _on_create_log(self):
        success, msg = backup_core.create_daily_log()
        self._show_result(success, msg, "Create Log")

    def _on_backup_paths(self):
        success, msg = backup_core.get_backup_paths()
        self._show_result(success, msg, "Backup Paths")


# --- Entry Point ---

def main():
    """GUI entry point."""
    root = tk.Tk()
    SmartBackupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
