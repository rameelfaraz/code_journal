"""
CustomTkinter-based GUI for Smart Backup Manager.
"""

import customtkinter as cctk
from tkinter import messagebox
import backup_core

# Configure appearance
cctk.set_appearance_mode("dark")
cctk.set_default_color_theme("blue")

class SmartBackupApp(cctk.CTk):
    """Main CustomTkinter application window."""
    def __init__(self):
        super().__init__()
        self.title("Smart Backup Manager")
        self.geometry("950x620")
        self.minsize(800, 520)

        # Center window
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()
        self._refresh_file_list()

    def _build_ui(self):
        # Grid layout: 1 row, 2 columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Left Sidebar
        self.sidebar = cctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(11, weight=1) # Spacer row

        # Header Title
        cctk.CTkLabel(
            self.sidebar,
            text="💾  Backup Manager",
            font=cctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 16), sticky="w")

        # Sidebar Buttons
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

        for idx, (text, cmd) in enumerate(buttons, start=1):
            btn = cctk.CTkButton(
                self.sidebar,
                text=text,
                anchor="w",
                font=cctk.CTkFont(family="Segoe UI", size=12),
                command=cmd
            )
            btn.grid(row=idx, column=0, padx=15, pady=4, sticky="ew")

        # Clear Output button
        self.clear_btn = cctk.CTkButton(
            self.sidebar,
            text="🧹  Clear Output",
            fg_color="gray30",
            hover_color="gray40",
            font=cctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._clear_output
        )
        self.clear_btn.grid(row=12, column=0, padx=15, pady=(10, 20), sticky="ew")

        # 2. Main Content Area
        self.content_frame = cctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.content_frame.grid_rowconfigure(2, weight=1) # Text box takes all free space
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Toolbar Section: File Selector & Refresh Button
        self.toolbar = cctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        cctk.CTkLabel(
            self.toolbar,
            text="Active File:",
            font=cctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(side="left", padx=(0, 8))

        self.file_dropdown = cctk.CTkOptionMenu(
            self.toolbar,
            values=["-- No files found --"],
            width=220,
            font=cctk.CTkFont(family="Segoe UI", size=12)
        )
        self.file_dropdown.pack(side="left", padx=(0, 8))

        self.refresh_btn = cctk.CTkButton(
            self.toolbar,
            text="🔄 Refresh",
            width=80,
            font=cctk.CTkFont(family="Segoe UI", size=12),
            command=self._refresh_file_list
        )
        self.refresh_btn.pack(side="left")

        # Header Info Row
        header_row = cctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        cctk.CTkLabel(
            header_row,
            text="Console Logs",
            font=cctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="left")

        # Scrollable console text area
        self.output_textbox = cctk.CTkTextbox(
            self.content_frame,
            font=cctk.CTkFont(family="Consolas", size=11),
            activate_scrollbars=True
        )
        self.output_textbox.grid(row=2, column=0, sticky="nsew")
        self.output_textbox.configure(state="disabled")

        # Status Bar Footer
        self.status_bar = cctk.CTkLabel(
            self.content_frame,
            text="Ready",
            anchor="w",
            font=cctk.CTkFont(family="Segoe UI", size=11)
        )
        self.status_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))

    # --- File List Handling ---

    def _refresh_file_list(self):
        """Fetch list of files in source_files and populate the option menu."""
        files = backup_core.get_source_files()
        if files:
            self.file_dropdown.configure(values=files)
            # Pick first file as active if current is default or not in list
            current = self.file_dropdown.get()
            if current not in files:
                self.file_dropdown.set(files[0])
        else:
            self.file_dropdown.configure(values=["-- No files found --"])
            self.file_dropdown.set("-- No files found --")

    def _get_selected_file(self):
        """Get the active file name from option menu."""
        val = self.file_dropdown.get()
        if val in ("", "-- No files found --"):
            return None
        return val

    # --- Output Helpers ---

    def _append_text(self, text):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", text + "\n")
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    def _show_result(self, success, message, title):
        self._append_text(f"--- {title} ---")
        prefix = "✓" if success else "✗"
        self._append_text(f"  {prefix} {message}\n")

        status_msg = f"  ✓ {title} completed successfully." if success else f"  ✗ {title} failed."
        status_color = "#4ade80" if success else "#f87171"
        self.status_bar.configure(text=status_msg, text_color=status_color)

    def _clear_output(self):
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")
        self.status_bar.configure(text="Ready", text_color="white")

    # --- Button Callbacks ---

    def _on_setup(self):
        success, msg = backup_core.setup_workspace()
        self._show_result(success, msg, "Setup Workspace")
        self._refresh_file_list()

    def _on_show_source(self):
        success, msg = backup_core.list_source_files()
        self._show_result(success, msg, "Source Files")
        self._refresh_file_list()

    def _on_timestamp_backup(self):
        fname = self._get_selected_file()
        if not fname:
            messagebox.showwarning("File Required", "Please select a file from the 'Active File' dropdown.")
            return

        success, msg = backup_core.create_timestamp_backup(fname)
        self._show_result(success, msg, "Timestamp Backup")

    def _on_quick_copy(self):
        fname = self._get_selected_file()
        if not fname:
            messagebox.showwarning("File Required", "Please select a file from the 'Active File' dropdown.")
            return

        overwrite = False
        if backup_core.quick_copy_exists(fname):
            overwrite = messagebox.askyesno(
                "File Exists",
                f"A quick copy of '{fname}' already exists in backups.\n\nDo you want to overwrite it?"
            )
            if not overwrite:
                self.status_bar.configure(text="  Quick Copy cancelled.", text_color="#fbbf24")
                return

        success, msg = backup_core.create_quick_copy(fname, overwrite=overwrite)
        self._show_result(success, msg, "Quick Copy")

    def _on_move_file(self):
        fname = self._get_selected_file()
        if not fname:
            messagebox.showwarning("File Required", "Please select a file from the 'Active File' dropdown.")
            return

        confirm = messagebox.askyesno(
            "Confirm Move",
            f"Are you sure you want to move '{fname}' to moved_files?\n\nThis deletes it from source_files."
        )
        if not confirm:
            self.status_bar.configure(text="  Move cancelled.", text_color="#fbbf24")
            return

        success, msg = backup_core.move_file(fname)
        self._show_result(success, msg, "Move File")
        self._refresh_file_list()

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

def main():
    app = SmartBackupApp()
    app.mainloop()

if __name__ == "__main__":
    main()
