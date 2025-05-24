import tkinter as tk
from tkinter import filedialog, ttk, font
import os
import sys
import json
import time
import threading
import random
import string

# Base directory for portability (handles PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
SESSION_FILE = os.path.join(BASE_DIR, "last_session.txt")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
README_FILENAME = os.path.join(BASE_DIR, "readme.txt")

# Theme definitions
NORD_BG = "#2e3440"
NORD_FG = "#d8dee9"

# Dark theme for menus and popups
MENU_THEME = {
    "bg": "#1e1e1e",
    "fg": "#d4d4d4",
    "active_bg": "#2a2a2a",
    "input_bg": "#1f1f1f"
}

THEMES = {
    "dark": {"bg": "#1e1e1e", "fg": "#d4d4d4", "insert": "#ffffff"},
    "paper": {"bg": "#f5f5f5", "fg": "#222222", "insert": "#222222"},
    "sepia": {"bg": "#f5e6c4", "fg": "#5b4636", "insert": "#5b4636"},
    "nord": {"bg": NORD_BG, "fg": NORD_FG, "insert": NORD_FG},
    "gruvbox_light": {"bg": "#fbf1c7", "fg": "#3c3836", "insert": "#3c3836"},
    "gruvbox_dark": {"bg": "#282828", "fg": "#ebdbb2", "insert": "#ebdbb2"},
    "monokai": {"bg": "#272822", "fg": "#f8f8f2", "insert": "#f8f8f2"},
    "cobalt": {"bg": "#002240", "fg": "#ffffff", "insert": "#ffffff"}
}

THEME_CHOICES = [
    "dark", "paper", "sepia", "nord", "gruvbox_light", "gruvbox_dark", "monokai", "cobalt", "custom"
]

# Font options
BASIC_FONT_FAMILIES = [
    "Arial", "Calibri", "Cambria", "Century", "Comic Sans", "Consolas",
    "Courier New", "Serif", "Times New Roman", "Verdana", "More Fonts..."
]

# Default settings
DEFAULT_SETTINGS = {
    "font_family": "Consolas",
    "full_font_family": "",
    "font_size": 16,
    "theme": "nord",
    "autosave_interval": 10,
    "max_char_width": 50,
    "typewriter_position": 0.55,
    "custom_bg": "#222222",
    "custom_fg": "#eaeaea",
    "show_word_count": False
}

README_TEXT = """Right click to see the context menu and hotkeys.
Open any text document, and it will auto open next time.
"""

class DistractionFreeWriter:
    def __init__(self, root):
        self.root = root
        self.settings = self.load_settings()
        self.current_file = None
        self.autosave_enabled = False
        self.previous_text = ""  # For tracking large deletions
        self.settings_window = None

        self.setup_window()
        self.build_layout()
        self.build_context_menu()
        self.bind_events()
        self.root.after(100, self.startup_session_restore)

    def setup_window(self):
        """Configure the main window."""
        self.root.title("Distraction-Free Writer")
        self.root.configure(bg=self.theme("bg"))
        self.root.attributes("-fullscreen", True)

    def bind_events(self):
        """Bind keyboard and mouse events."""
        self.root.bind("<Escape>", lambda event: self.root.destroy())
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Control-o>", self.open_file_dialog)
        self.root.bind("<Control-s>", self.save_as_dialog)
        self.root.bind("<F12>", self.open_settings_editor)
        self.root.bind("<Configure>", self.on_window_resize)
        self.text_area.bind("<Button-3>", self.show_context_menu)
        self.container.bind("<Button-3>", self.show_context_menu)
        self.text_area.bind("<<Modified>>", self.on_text_modified)

    def build_context_menu(self):
        """Create the right-click context menu."""
        self.context_menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=MENU_THEME["bg"],
            fg=MENU_THEME["fg"],
            activebackground=MENU_THEME["active_bg"],
            activeforeground=MENU_THEME["fg"],
            selectcolor=MENU_THEME["bg"],
            bd=0,
            font=("Segoe UI", 11)
        )
        self.context_menu.add_command(label="Settings - F12", command=self.open_settings_editor)
        self.context_menu.add_command(label="Save - Ctrl+S", command=self.save_as_dialog)
        self.context_menu.add_command(label="Open - Ctrl+O", command=self.open_file_dialog)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Fullscreen - F11", command=self.toggle_fullscreen)
        self.context_menu.add_command(label="Exit - Esc", command=self.root.destroy)
        self.update_context_menu_theme()

    def update_context_menu_theme(self):
        """Apply dark theme to context menu."""
        try:
            self.context_menu.configure(
                bg=MENU_THEME["bg"],
                fg=MENU_THEME["fg"],
                activebackground=MENU_THEME["active_bg"],
                activeforeground=MENU_THEME["fg"],
                selectcolor=MENU_THEME["bg"],
                bd=0,
                font=("Segoe UI", 11)
            )
        except tk.TclError:
            pass

    def show_context_menu(self, event):
        """Display the context menu at the cursor position."""
        self.update_context_menu_theme()
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def theme(self, key):
        """Retrieve theme properties for editor."""
        if self.settings.get("theme") == "custom":
            return {
                "bg": self.settings.get("custom_bg", "#222222"),
                "fg": self.settings.get("custom_fg", "#eaeaea"),
                "insert": self.settings.get("custom_fg", "#eaeaea")
            }.get(key, "#000000")
        return THEMES.get(self.settings["theme"], THEMES["nord"]).get(key, "#000000")

    def get_font_family(self):
        """Determine the current font family."""
        if self.settings.get("font_family") == "More Fonts...":
            return self.settings.get("full_font_family") or BASIC_FONT_FAMILIES[0]
        return self.settings.get("font_family", BASIC_FONT_FAMILIES[0])

    def load_settings(self):
        """Load settings from file or return defaults."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return {**DEFAULT_SETTINGS, **json.load(f)}
            except (json.JSONDecodeError, IOError):
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """Save settings to file."""
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            pass

    def apply_settings(self):
        """Apply current settings to the UI."""
        bg = self.theme("bg")
        fg = self.theme("fg")
        self.root.configure(bg=bg)
        self.container.configure(bg=bg)
        self.text_area.configure(
            font=(self.get_font_family(), self.settings["font_size"]),
            bg=bg,
            fg=fg,
            wrap="word",
            width=self.settings.get("max_char_width", 50)
        )
        self.word_count_label.configure(bg=bg, fg=fg)
        self.center_text_area()
        self.update_context_menu_theme()
        if self.settings_window and self.settings_window.winfo_exists():
            self.update_settings_window_theme(self.settings_window)
        self.update_word_count_label()

    def build_layout(self):
        """Create the main UI layout."""
        self.container = tk.Frame(self.root, bg=self.theme("bg"))
        self.container.pack(fill="both", expand=True)

        self.text_area = tk.Text(
            self.container,
            wrap="word",
            font=(self.get_font_family(), self.settings["font_size"]),
            bg=self.theme("bg"),
            fg=self.theme("fg"),
            undo=True,
            width=self.settings.get("max_char_width", 50),
            bd=0
        )
        self.text_area.pack(side="top", anchor="center", pady=0)

        self.word_count_label = tk.Label(
            self.container,
            bg=self.theme("bg"),
            fg=self.theme("fg"),
            anchor="e",
            font=("Segoe UI", 12),
            bd=0
        )
        self.word_count_label.place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-10)
        self.update_word_count_label()
        self.center_text_area()

    def center_text_area(self, event=None):
        """Center the text area horizontally and vertically."""
        self.root.update_idletasks()
        win_h = self.container.winfo_height()
        win_w = self.container.winfo_width()
        typewriter_pos = float(self.settings.get("typewriter_position", 0.55))
        try:
            line_height = self.text_area.dlineinfo("1.0")[3]
        except (tk.TclError, TypeError):
            line_height = self.settings.get("font_size", 18) + 4
        lines = int(win_h * typewriter_pos) // line_height
        self.text_area.config(height=lines)

        font_obj = font.Font(family=self.get_font_family(), size=self.settings["font_size"])
        char_width = font_obj.measure("M")
        text_width = char_width * self.settings.get("max_char_width", 50)
        padx = max(0, (win_w - text_width) // 2)

        self.text_area.pack_configure(padx=padx, pady=0, anchor="center")

    def update_word_count_label(self, event=None):
        """Update the word count display."""
        if self.settings.get("show_word_count", False):
            text = self.text_area.get("1.0", "end-1c")
            word_count = len(text.split())
            self.word_count_label.config(text=f"{word_count} words")
            self.word_count_label.lift()
            self.word_count_label.place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-10)
        else:
            self.word_count_label.config(text="")
            self.word_count_label.place_forget()

    def on_window_resize(self, event):
        """Handle window resize events."""
        self.center_text_area()
        self.update_word_count_label()

    def startup_session_restore(self):
        """Load the last session or create a readme file."""
        if not os.path.exists(SESSION_FILE):
            self.create_readme()
        else:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                last_path = f.read().strip()
            if last_path and os.path.isfile(last_path):
                self.load_file(last_path)
                self.autosave_enabled = True
                threading.Thread(target=self.autosave_loop, daemon=True).start()
                self.root.after(150, self.scroll_to_bottom_and_center)
                return
            self.create_readme()

    def create_readme(self):
        """Create and load the readme file if no session exists."""
        if not os.path.isfile(README_FILENAME):
            with open(README_FILENAME, "w", encoding="utf-8") as f:
                f.write(README_TEXT)
        self.load_file(README_FILENAME)
        self.current_file = README_FILENAME
        self.save_session(README_FILENAME)
        self.autosave_enabled = True
        threading.Thread(target=self.autosave_loop, daemon=True).start()
        self.root.after(150, self.scroll_to_bottom_and_center)

    def scroll_to_bottom_and_center(self):
        """Scroll to the bottom of the text area and center the cursor."""
        self.text_area.mark_set("insert", "end-1c")
        self.text_area.focus_set()
        self.text_area.see("insert")

    def save_session(self, file_path):
        """Save the current file path for session restoration."""
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                f.write(file_path)
        except IOError:
            pass

    def load_file(self, file_path):
        """Load a file into the text area."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", content)
                self.previous_text = content
            self.current_file = file_path
            self.save_session(file_path)
            self.update_word_count_label()
        except (IOError, UnicodeDecodeError) as e:
            tk.messagebox.showerror("Error", f"Could not load file:\n{str(e)}")
            self.root.destroy()

    def save_file(self, file_path):
        """Save the text area content to a file."""
        try:
            content = self.text_area.get("1.0", "end-1c")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.current_file = file_path
            self.save_session(file_path)
            self.previous_text = content
        except IOError as e:
            tk.messagebox.showerror("Error", f"Could not save file:\n{str(e)}")

    def create_backup_file(self):
        """Create a backup file if a large deletion occurs."""
        if not self.current_file:
            return
        try:
            content = self.previous_text
            base, ext = os.path.splitext(self.current_file)
            random_suffix = ''.join(random.choices(string.digits, k=4))
            backup_path = f"{base}_backup_{random_suffix}{ext}"
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)
        except IOError as e:
            tk.messagebox.showerror("Error", f"Could not create backup file:\n{str(e)}")

    def open_file_dialog(self, event=None, force_prompt=False):
        """Open a file dialog to select a text file."""
        file_path = filedialog.askopenfilename(
            initialdir=BASE_DIR,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Open Text File"
        )
        if file_path:
            if not os.path.abspath(file_path).startswith(BASE_DIR):
                tk.messagebox.showerror("Error", "All files must be inside the app folder for portability.")
                self.open_file_dialog(force_prompt=force_prompt)
                return
            self.load_file(file_path)
            self.current_file = file_path
            self.autosave_enabled = True
            threading.Thread(target=self.autosave_loop, daemon=True).start()
            self.root.after(150, self.scroll_to_bottom_and_center)
            self.update_word_count_label()
        elif force_prompt:
            tk.messagebox.showinfo("No File Selected", "No file selected. Exiting.")
            self.root.destroy()

    def save_as_dialog(self, event=None):
        """Open a save dialog to save the current text."""
        file_path = filedialog.asksaveasfilename(
            initialdir=BASE_DIR,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save As"
        )
        if file_path:
            if not os.path.abspath(file_path).startswith(BASE_DIR):
                tk.messagebox.showerror("Error", "All files must be inside the app folder for portability.")
                self.save_as_dialog()
                return
            self.save_file(file_path)
            self.current_file = file_path
            self.autosave_enabled = True

    def autosave_loop(self):
        """Periodically save the current file."""
        while True:
            time.sleep(self.settings.get("autosave_interval", 10))
            if self.current_file and self.autosave_enabled:
                self.save_file(self.current_file)

    def on_text_modified(self, event=None):
        """Handle text modifications, including large deletions."""
        if self.text_area.edit_modified():
            current_text = self.text_area.get("1.0", "end-1c")
            if len(self.previous_text) - len(current_text) > 3000:
                self.create_backup_file()
            self.previous_text = current_text
            self.text_area.edit_modified(False)
        self.update_word_count_label()

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        current = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current)

    def update_settings_window_theme(self, win):
        """Apply dark theme to the settings window."""
        bg = MENU_THEME["bg"]
        fg = MENU_THEME["fg"]
        active_bg = MENU_THEME["active_bg"]
        input_bg = MENU_THEME["input_bg"]
        for child in win.winfo_children():
            if isinstance(child, tk.Entry):
                child.configure(background=input_bg, foreground=fg, width=22)
            elif isinstance(child, ttk.Combobox):
                child.configure(style="CustomTheme.TCombobox")
            elif isinstance(child, tk.Label):
                child.configure(background=bg, foreground=fg)
            elif isinstance(child, tk.Checkbutton):
                child.configure(background=bg, foreground=fg, selectcolor=bg, activebackground=bg, activeforeground=fg)
            elif isinstance(child, tk.Frame):
                child.configure(background=bg)
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Button):
                        subchild.configure(background=bg, foreground=fg, activebackground=active_bg)
        win.configure(background=bg)

    def open_settings_editor(self, event=None):
        """Open the settings editor window."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.update_settings_window_theme(self.settings_window)
            return

        win = tk.Toplevel(self.root)
        self.settings_window = win
        win.title("Settings Editor")
        win.geometry("480x600")
        win.configure(bg=MENU_THEME["bg"])
        entries = {}
        base_row = 2

        style = ttk.Style(win)
        style.theme_use('default')
        style.configure("CustomTheme.TCombobox",
                        fieldbackground=MENU_THEME["input_bg"],
                        background=MENU_THEME["input_bg"],
                        foreground=MENU_THEME["fg"])
        style.map("CustomTheme.TCombobox",
                  fieldbackground=[('readonly', MENU_THEME["input_bg"])],
                  background=[('readonly', MENU_THEME["input_bg"])],
                  selectbackground=[('readonly', MENU_THEME["active_bg"])],
                  selectforeground=[('readonly', MENU_THEME["fg"])])

        current_row = 0

        tk.Label(win, text="Font Family", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"]).grid(row=current_row, column=0, sticky="e", padx=8, pady=8)
        font_family_cb = ttk.Combobox(win, values=BASIC_FONT_FAMILIES, state="readonly", style="CustomTheme.TCombobox", width=20)
        font_family_cb.grid(row=current_row, column=1, sticky="w", padx=8, pady=8)
        font_family_cb.set(self.settings.get("font_family") if self.settings.get("font_family") in BASIC_FONT_FAMILIES else BASIC_FONT_FAMILIES[0])
        entries["font_family"] = font_family_cb

        full_font_cb = None

        def show_more_fonts(event=None):
            nonlocal full_font_cb, base_row
            if font_family_cb.get() == "More Fonts...":
                fonts = sorted(list(font.families())) or ["Arial"]
                if full_font_cb:
                    full_font_cb.destroy()
                full_font_cb = ttk.Combobox(win, values=fonts, state="readonly", style="CustomTheme.TCombobox", width=30)
                full_font_cb.set(self.settings.get("full_font_family") or fonts[0])
                full_font_cb.grid(row=current_row+1, column=1, sticky="w", padx=8, pady=8)
                tk.Label(win, text="Pick a font", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"]).grid(row=current_row+1, column=0, sticky="e", padx=8, pady=8)
                entries["full_font_family"] = full_font_cb
                base_row = 3
            else:
                if full_font_cb:
                    full_font_cb.destroy()
                    full_font_cb = None
                entries["full_font_family"] = None
                base_row = 2
            update_layout()

        font_family_cb.bind("<<ComboboxSelected>>", show_more_fonts)

        tk.Label(win, text="Font Size", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"]).grid(row=base_row, column=0, sticky="e", padx=8, pady=8)
        font_size_entry = tk.Entry(win, background=MENU_THEME["input_bg"], foreground=MENU_THEME["fg"], width=20)
        font_size_entry.insert(0, str(self.settings.get("font_size", "")))
        font_size_entry.grid(row=base_row, column=1, sticky="w", padx=8, pady=8)
        entries["font_size"] = font_size_entry

        tk.Label(win, text="Theme", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"]).grid(row=base_row+1, column=0, sticky="e", padx=8, pady=8)
        theme_cb = ttk.Combobox(win, values=THEME_CHOICES, state="readonly", style="CustomTheme.TCombobox", width=20)
        theme_cb.set(self.settings.get("theme", "nord"))
        theme_cb.grid(row=base_row+1, column=1, sticky="w", padx=8, pady=8)
        entries["theme"] = theme_cb

        custom_bg_label = tk.Label(win, text="Custom BG (#xxxxxx)", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"])
        custom_bg_entry = tk.Entry(win, background=MENU_THEME["input_bg"], foreground=MENU_THEME["fg"], width=20)
        custom_bg_entry.insert(0, self.settings.get("custom_bg", "#222222"))
        entries["custom_bg"] = custom_bg_entry

        custom_fg_label = tk.Label(win, text="Custom FG (#xxxxxx)", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"])
        custom_fg_entry = tk.Entry(win, background=MENU_THEME["input_bg"], foreground=MENU_THEME["fg"], width=20)
        custom_fg_entry.insert(0, self.settings.get("custom_fg", "#eaeaea"))
        entries["custom_fg"] = custom_fg_entry

        autosave_label = tk.Label(win, text="Autosave Interval (sec)", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"])
        autosave_entry = tk.Entry(win, background=MENU_THEME["input_bg"], foreground=MENU_THEME["fg"], width=20)
        autosave_entry.insert(0, str(self.settings.get("autosave_interval", "")))
        entries["autosave_interval"] = autosave_entry

        maxchar_label = tk.Label(win, text="Max Char Width", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"])
        maxchar_entry = tk.Entry(win, background=MENU_THEME["input_bg"], foreground=MENU_THEME["fg"], width=20)
        maxchar_entry.insert(0, str(self.settings.get("max_char_width", "")))
        entries["max_char_width"] = maxchar_entry

        typewriter_label = tk.Label(win, text="Typewriter Position", background=MENU_THEME["bg"], foreground=MENU_THEME["fg"])
        typewriter_entry = tk.Entry(win, background=MENU_THEME["input_bg"], foreground=MENU_THEME["fg"], width=20)
        typewriter_entry.insert(0, str(self.settings.get("typewriter_position", "")))
        entries["typewriter_position"] = typewriter_entry

        show_word_count_var = tk.BooleanVar(value=self.settings.get("show_word_count", False))
        word_count_cb = tk.Checkbutton(
            win,
            text="Show Word Count (bottom right)",
            variable=show_word_count_var,
            bg=MENU_THEME["bg"],
            fg=MENU_THEME["fg"],
            selectcolor=MENU_THEME["bg"],
            activebackground=MENU_THEME["bg"],
            activeforeground=MENU_THEME["fg"]
        )
        entries["show_word_count"] = show_word_count_var

        button_frame = tk.Frame(win, bg=MENU_THEME["bg"])
        apply_button = tk.Button(
            button_frame,
            text="Apply",
            command=lambda: apply_changes(),
            background=MENU_THEME["bg"],
            foreground=MENU_THEME["fg"],
            activebackground=MENU_THEME["active_bg"],
            width=8
        )
        apply_button.pack(side="left", padx=10)
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=win.destroy,
            background=MENU_THEME["bg"],
            foreground=MENU_THEME["fg"],
            activebackground=MENU_THEME["active_bg"],
            width=8
        )
        close_button.pack(side="left", padx=10)

        def update_layout():
            """Update the layout based on current settings."""
            nonlocal base_row
            other_row = base_row + 2

            # Clear existing custom fields
            for widget in [custom_bg_label, custom_bg_entry, custom_fg_label, custom_fg_entry]:
                widget.grid_remove()

            # Show custom fields if custom theme is selected
            if entries["theme"].get() == "custom":
                custom_bg_label.grid(row=base_row+2, column=0, sticky="e", padx=8, pady=8)
                custom_bg_entry.grid(row=base_row+2, column=1, sticky="w", padx=8, pady=8)
                custom_fg_label.grid(row=base_row+3, column=0, sticky="e", padx=8, pady=8)
                custom_fg_entry.grid(row=base_row+3, column=1, sticky="w", padx=8, pady=8)
                other_row = base_row + 4
            else:
                other_row = base_row + 2

            # Grid other settings
            autosave_label.grid(row=other_row, column=0, sticky="e", padx=8, pady=8)
            autosave_entry.grid(row=other_row, column=1, sticky="w", padx=8, pady=8)
            maxchar_label.grid(row=other_row+1, column=0, sticky="e", padx=8, pady=8)
            maxchar_entry.grid(row=other_row+1, column=1, sticky="w", padx=8, pady=8)
            typewriter_label.grid(row=other_row+2, column=0, sticky="e", padx=8, pady=8)
            typewriter_entry.grid(row=other_row+2, column=1, sticky="w", padx=8, pady=8)
            word_count_cb.grid(row=other_row+3, column=0, columnspan=2, pady=(10, 10), sticky="w")
            button_frame.grid(row=other_row+4, column=0, columnspan=2, pady=15, sticky="ew")

        def show_custom_fields(event=None):
            """Show or hide custom theme fields."""
            update_layout()

        def apply_changes():
            """Apply settings from the editor."""
            try:
                font_choice = entries["font_family"].get()
                self.settings["font_family"] = font_choice
                self.settings["full_font_family"] = entries.get("full_font_family", None).get() if font_choice == "More Fonts..." and entries.get("full_font_family") else ""
                self.settings["font_size"] = int(entries["font_size"].get())
                self.settings["theme"] = entries["theme"].get().strip()
                self.settings["autosave_interval"] = int(entries["autosave_interval"].get())
                self.settings["max_char_width"] = int(entries["max_char_width"].get())
                self.settings["typewriter_position"] = float(entries["typewriter_position"].get())
                self.settings["show_word_count"] = bool(entries["show_word_count"].get())
                if self.settings["theme"] == "custom":
                    self.settings["custom_bg"] = entries["custom_bg"].get().strip()
                    self.settings["custom_fg"] = entries["custom_fg"].get().strip()
                self.save_settings()
                self.apply_settings()
            except (ValueError, tk.TclError) as e:
                tk.messagebox.showerror("Error", f"Invalid input: {str(e)}")

        theme_cb.bind("<<ComboboxSelected>>", show_custom_fields)
        show_more_fonts()  # Initialize font selection
        show_custom_fields()  # Initialize theme settings

        win.grid_columnconfigure(0, weight=1, uniform="x")
        win.grid_columnconfigure(1, weight=2, uniform="x")

        self.update_settings_window_theme(win)

if __name__ == "__main__":
    root = tk.Tk()
    app = DistractionFreeWriter(root)
    root.mainloop()
