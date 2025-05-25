# Void Writer - A Distraction-Free Writer
<img src="https://github.com/deminimis/voidwriter/blob/main/assets/logo.png" alt="Description" width="200">

**Void Writer** is a minimalist, cross-platform text editor built with Python3 with no other dependencies, designed for writers seeking a focused, distraction-free environment. Leveraging a lightweight architecture and a robust feature set, it provides a seamless writing experience that is themeable, has session persistence, and portability. 


## Features

- **Minimalist UI**: A fullscreen, centered text area eliminates distractions, with configurable line width and typewriter-style positioning for ergonomic writing.
- **Cross-Platform Portability**: Uses a single Python script with no external dependencies beyond the standard library (Tkinter 8.5+).
- **Theming System**: Supports multiple editor themes (`dark`, `paper`, `sepia`, `nord`, `gruvbox_light`, `gruvbox_dark`, `monokai`, `cobalt`, `custom`) with customizable background and foreground colors. Menus and popups use a consistent dark theme for visual coherence.
- **Session Persistence**: Automatically saves and restores the last opened file via a session file (`last_session.txt`).
- **Autosave**: Configurable autosave intervals (default: 10 seconds) ensure data integrity without manual intervention, implemented via a background threading loop.
- **Backup on Large Deletions**: Automatically creates backup files for deletions exceeding 3000 characters, appending a random 4-digit suffix to prevent data loss.
- **Customizable Settings**:
  - Font family (from system fonts or predefined options like `Consolas`, `Arial`) and size.
  - Maximum character width for text wrapping.
  - Typewriter position (vertical alignment as a percentage of window height).
  - Optional word count display in the bottom-right corner.
- **Context Menu**: Right-click access to settings, save, open, fullscreen toggle, and exit, styled with a dark theme for consistency.
- **Hotkey Support**: Intuitive shortcuts (`Ctrl+O` for open, `Ctrl+S` for save, `F12` for settings, `F11` for fullscreen, `Esc` to exit) enhance productivity.
- **Undo Support**: Built-in undo stack for the text area, preserving editing history.
- **Responsive Layout**: Dynamically centers the text area based on window size and font metrics, ensuring optimal readability.

<img src="https://github.com/deminimis/voidwriter/blob/main/assets/screenshot1.png" alt="Description" width="750">
<img src="https://github.com/deminimis/voidwriter/blob/main/assets/screenshot3.png" alt="Description" width="1000"> <img src="https://github.com/deminimis/voidwriter/blob/main/assets/screenshot2.png" alt="Description" width="1000">

## Installation

### Windows

1. You can just download the provided .exe.

2. Alternatively, just download the writer.py and open (requires python 3). 

### Linux
1. **Prerequisites**: Python 3 with Tkinter (included on Windows and most Linux distributions).

2. Download the .py

3. Run the .py



## Usage
1. **Launch**: The editor opens in fullscreen mode with the last session’s file. Open any file you want with ctrl+o (or right click).
2. **Context Menu**: Right-click to access options (Settings, Save, Open, Toggle Fullscreen, Exit).
3. **Settings**:
   - Press `F12` or right click to open the settings popup.
   - Configure font, theme, autosave interval, text width, typewriter position, and word count display.
   - Custom themes allow hex color inputs for background and foreground.
   - Click "Apply" to save changes or "Close" to discard.
4. **Hotkeys**:
   - `Ctrl+O`: Open a file.
   - `Ctrl+S`: Save as.
   - `F11`: Toggle fullscreen.
   - `F12`: Open settings.
   - `Esc`: Exit.
5. **File Management**:
   - Keep files in the same folder for portability.
   - Autosave runs every 10 seconds, which can be changed in settings.
   - Large deletions (>3000 characters) trigger backups.

## Configuration
Settings are stored in `settings.json` and include:
- `font_family`: Font name (e.g., `Consolas`) or `More Fonts...` for system fonts.
- `full_font_family`: Selected system font if `font_family` is `More Fonts...`.
- `font_size`: Integer (e.g., `16`).
- `theme`: One of `dark`, `paper`, `sepia`, `nord`, `gruvbox_light`, `gruvbox_dark`, `monokai`, `cobalt`, `custom`.
- `autosave_interval`: Seconds between autosaves (e.g., `10`).
- `max_char_width`: Maximum characters per line (e.g., `50`).
- `typewriter_position`: Vertical alignment (0.0 to 1.0, e.g., `0.55`).
- `custom_bg`, `custom_fg`: Hex colors for custom theme (e.g., `#222222`, `#eaeaea`).
- `show_word_count`: Boolean to display word count.

Example `settings.json`:
```json
{
  "font_family": "Consolas",
  "font_size": 16,
  "theme": "nord",
  "autosave_interval": 10,
  "max_char_width": 50,
  "typewriter_position": 0.55,
  "show_word_count": true
}
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

Potential enhancements (or distractions):
- Markdown or rich text support.
- Spell-checking integration.
- Additional themes or font options.
- Export to PDF or other formats.



## License
This project is licensed under the MIT License.

