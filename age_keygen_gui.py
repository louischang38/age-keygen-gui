#!/usr/bin/env python3

import sys
import os
import subprocess
import platform
from shutil import which
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
    QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont, QColor, QIcon, QTextCursor, QTextCharFormat, QGuiApplication
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QSize

import darkdetect

# ==========================================
# 🎨 Theme Manager
# ==========================================
class ThemeManager:
    @staticmethod
    def get_font_families():
        system = platform.system()
        if system == "Windows":
            return ["Microsoft YaHei UI", "Segoe UI", "Arial", "Helvetica", "sans-serif"]
        elif system == "Darwin":
            return ["PingFang TC", "Helvetica Neue", "SF Pro Text", "Arial", "sans-serif"]
        else:
            return ["Noto Sans CJK TC", "Roboto", "Ubuntu", "Arial", "sans-serif"]

    LIGHT_THEME = {
        "name": "light",
        "colors": {
            "PRIMARY": "#007AFF", "PRIMARY_HOVER": "#0056CC", "SECONDARY": "#5856D6",
            "BACKGROUND": "#F2F2F7", "CARD_BG": "#FFFFFF", "TEXT_PRIMARY": "#000000",
            "TEXT_SECONDARY": "#8E8E93", "TEXT_DISABLED": "#C7C7CC", "BORDER": "#C7C7CC",
            "SUCCESS": "#34C759", "WARNING": "#FF9500", "ERROR": "#FF3B30", "HIGHLIGHT": "#FFF2CC",
        }
    }

    DARK_THEME = {
        "name": "dark",
        "colors": {
            "PRIMARY": "#0A84FF", "PRIMARY_HOVER": "#409CFF", "SECONDARY": "#5E5CE6",
            "BACKGROUND": "#000000", "CARD_BG": "#1C1C1E", "TEXT_PRIMARY": "#FFFFFF",
            "TEXT_SECONDARY": "#8E8E93", "TEXT_DISABLED": "#48484A", "BORDER": "#38383A",
            "SUCCESS": "#30D158", "WARNING": "#FF9F0A", "ERROR": "#FF453A", "HIGHLIGHT": "#2C2C2E",
        }
    }

    @classmethod
    def get_current_theme(cls):
        return cls.DARK_THEME if darkdetect.isDark() else cls.LIGHT_THEME

    @classmethod
    def get_stylesheet(cls):
        theme = cls.get_current_theme()
        colors = theme["colors"]
        font_families = ", ".join(cls.get_font_families())
        return f"""
            * {{ font-family: {font_families}; font-size: 13px; outline: none; }}
            QMainWindow, QWidget#CentralWidget {{ 
                background-color: {colors['BACKGROUND']}; 
                border: none; 
                border-radius: 0;
            }}
            QLabel {{ color: {colors['TEXT_PRIMARY']}; font-size: 14px; font-weight: 500; }}
            QLabel#HintLabel {{ font-size: 12px; font-weight: 400; color: {colors['TEXT_SECONDARY']}; font-style: italic; padding-left: 8px; }}
            
            QLabel#StatusLabel {{ 
                font-size: 12px; 
                font-weight: 500; 
                color: {colors['TEXT_SECONDARY']}; 
                padding: 10px 0;
            }}

            QTextEdit {{ background-color: {colors['CARD_BG']}; border: 1px solid {colors['BORDER']}; border-radius: 8px;
                        font-family: "SF Mono", "Cascadia Mono", "Consolas", monospace; 
                        font-size: 12px; 
                        padding: 10px;
                        color: {colors['TEXT_PRIMARY']};
                        selection-background-color: {colors['PRIMARY']}; selection-color: white; }}
            QTextEdit:focus {{ border: 2px solid {colors['PRIMARY']}; padding: 9px; }}
            
            QPushButton {{ border-radius: 8px; font-weight: 600; padding: 8px 16px; color: {colors['TEXT_PRIMARY']};
                          border: 1px solid {colors['BORDER']}; background-color: {colors['CARD_BG']}; min-height: 28px; }}
            QPushButton:hover {{ background-color: {colors['BORDER']}; }}
            QPushButton:pressed {{ background-color: {colors['TEXT_SECONDARY']}; }}
            QPushButton:disabled {{ color: {colors['TEXT_DISABLED']}; background-color: {colors['BACKGROUND']}; border-color: {colors['TEXT_DISABLED']}; }}
            
            /* PrimaryButton style adapted to use monochrome theme colors (Black/White or Dark Gray/White) */
            QPushButton#PrimaryButton {{ 
                background-color: {colors['TEXT_PRIMARY']}; 
                color: {colors['CARD_BG']}; 
                border: none; 
                padding: 12px 28px;
                font-size: 15px; font-weight: 600; min-height: 44px; 
            }}
            QPushButton#PrimaryButton:hover {{ 
                background-color: {colors['BORDER']}; 
                color: {colors['TEXT_PRIMARY']}; 
            }}
            QPushButton#PrimaryButton:pressed {{ background-color: {colors['TEXT_SECONDARY']}; }}
            QPushButton#PrimaryButton:disabled {{ background-color: {colors['TEXT_DISABLED']}; color: {colors['CARD_BG']}; }}
            
            QPushButton#SecondaryButton {{ font-size: 12px; padding: 6px 12px; border-radius: 6px; background-color: transparent;
                                           border: 1px solid {colors['BORDER']}; min-height: 24px; 
                                           }}
            QPushButton#SecondaryButton:hover {{ background-color: {colors['BORDER']}; }}
            QProgressBar {{ border: 1px solid {colors['BORDER']}; border-radius: 4px; background-color: {colors['CARD_BG']}; text-align: center; }}
            QProgressBar::chunk {{ background-color: {colors['PRIMARY']}; border-radius: 4px; }}
            QMessageBox {{ background-color: {colors['CARD_BG']}; }}
            QMessageBox QLabel {{ color: {colors['TEXT_PRIMARY']}; font-size: 14px; }}
        """

    @classmethod
    def get_colors(cls):
        return cls.get_current_theme()["colors"]

# ==========================================
# 🔧 Utility Functions
# ==========================================
def find_age_keygen():
    exe_name = "age-keygen.exe" if os.name == "nt" else "age-keygen"
    if os.path.exists(exe_name):
        return os.path.abspath(exe_name)
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        candidate = os.path.join(base_path, exe_name)
        if os.path.exists(candidate):
            return candidate
    path = which("age-keygen")
    if path:
        return path
    return None

# ==========================================
# ⚡ Async Worker
# ==========================================
class KeyGenerationWorker(QObject):
    started = Signal()
    progress = Signal(str)
    finished = Signal(str, str, str)
    error = Signal(str)

    def __init__(self, age_keygen_path, strings):
        super().__init__()
        self.age_keygen_path = age_keygen_path
        self.strings = strings

    def run(self):
        self.started.emit()
        self.progress.emit(self.strings["STATUS_INITIALIZING"])
        private_key = ""
        public_key = ""
        error_msg = ""
        try:
            self.progress.emit(self.strings["STATUS_RUNNING"])
            # Run age-keygen tool
            result = subprocess.run([self.age_keygen_path], capture_output=True, text=True, timeout=30, check=True)
            output = result.stdout + result.stderr
            
            # Extract Private Key
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("AGE-SECRET-KEY-"):
                    private_key = line
                    break
            
            if not private_key:
                error_msg = self.strings["ERROR_NO_PRIVATE_KEY"]
                self.error.emit(error_msg)
                self.finished.emit("", "", error_msg)
                return
            
            self.progress.emit(self.strings["STATUS_EXTRACTING_PUBLIC"])
            
            # Extract Public Key
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("age1"):
                    public_key = line
                    break
                elif line.startswith("# public key:"):
                    public_key = line.replace("# public key:", "").strip()
                    break
            
            if not public_key:
                self.progress.emit(self.strings["STATUS_EXPORTING_PUBLIC"])
                public_key = self._derive_public_key(private_key)
            
            self.progress.emit(self.strings["STATUS_DONE"])
            self.finished.emit(private_key, public_key, "")
            
        except subprocess.TimeoutExpired:
            error_msg = self.strings["ERROR_TIMEOUT"]
            self.error.emit(error_msg)
            self.finished.emit("", "", error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"{self.strings['ERROR_SUBPROCESS']}: {e.stderr.strip() or 'unknown output'}"
            self.error.emit(error_msg)
            self.finished.emit("", "", error_msg)
        except Exception as e:
            error_msg = f"{self.strings['ERROR_UNKNOWN']}: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit("", "", error_msg)

    def _derive_public_key(self, private_key):
        try:
            result = subprocess.run([self.age_keygen_path, '-y'], input=private_key.encode('utf-8'),
                                     capture_output=True, text=True, timeout=10, check=True)
            return result.stdout.strip()
        except Exception:
            return self.strings["ERROR_EXPORT_PUBLIC"]

# ==========================================
# 🪟 Main Window
# ==========================================
class AgeKeyGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.age_keygen_path = None
        self.generation_thread = None
        self.worker = None
        # Load English strings
        self.strings = self._load_strings()
        self._find_age_keygen()
        self._setup_window()
        self.colors = ThemeManager.get_colors()
        self._init_ui()
        self._apply_theme()
        self._connect_signals()
        
        self._drag_position = None

    def _load_strings(self):
        return {
            "TITLE": "Age Key Generator", 
            "BTN_GENERATE": "Generate New Key Pair", 
            "BTN_COPY": "Copy",
            "BTN_SAVE": "Save",
            "LBL_PRIVATE": "Private Key (Identity Key)",
            "LBL_PUBLIC": "Public Key (Recipient Key)",
            "HINT_PRIVATE": "Keep it safe and never share it.",
            "HINT_PUBLIC": "Can be shared safely.",
            "PLACEHOLDER_PRIVATE": "Click 'Generate New Key Pair' to create a Private Key...",
            "PLACEHOLDER_PUBLIC": "The Public Key will be displayed here...",
            "STATUS_READY": "Ready",
            "STATUS_GENERATING": "Generating Key...",
            "STATUS_SUCCESS": "Key Generation Successful!",
            "STATUS_ERROR": "An Error Occurred",
            "MSG_COPY_SUCCESS": "Copied to clipboard",
            "MSG_SAVE_SUCCESS": "File saved successfully",
            "MSG_NO_KEY": "Please generate a valid key first",
            "MSG_AGE_NOT_FOUND": "age-keygen not found. Please ensure age is installed.",
            "MSG_GENERATING": "Generating key. Please wait...",
            "ERROR_TITLE": "Error",
            "INFO_TITLE": "Information",
            "WARNING_TITLE": "Warning",
            "STATUS_INITIALIZING": "Initializing...",
            "STATUS_RUNNING": "Executing age-keygen...",
            "STATUS_EXTRACTING_PUBLIC": "Extracting Public Key...",
            "STATUS_EXPORTING_PUBLIC": "Exporting Public Key...",
            "STATUS_DONE": "Done!",
            "ERROR_NO_PRIVATE_KEY": "No valid Private Key found",
            "ERROR_EXPORT_PUBLIC": "Unable to derive Public Key",
            "ERROR_TIMEOUT": "Operation timed out. Please try again.",
            "ERROR_SUBPROCESS": "age-keygen execution failed",
            "ERROR_UNKNOWN": "An unexpected error occurred",
            "BTN_CLOSE": "Close",
        }

    def _find_age_keygen(self):
        self.age_keygen_path = find_age_keygen()
        if not self.age_keygen_path:
            QMessageBox.critical(self, self.strings["ERROR_TITLE"], self.strings["MSG_AGE_NOT_FOUND"])
            sys.exit(1)
        if not os.access(self.age_keygen_path, os.X_OK) and platform.system() != "Windows":
            try:
                os.chmod(self.age_keygen_path, 0o755)
            except:
                QMessageBox.critical(self, self.strings["ERROR_TITLE"], f"No execute permission: {self.age_keygen_path}")
                sys.exit(1)

    def _setup_window(self):
        self.setWindowTitle(self.strings["TITLE"])
        self.setFixedSize(650, 400) 
        self._set_window_icon()

    def _set_window_icon(self):
        icon_paths = ["icon.ico", "icon.png", os.path.join(os.path.dirname(__file__), "icon.ico")]
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            icon_paths.insert(0, os.path.join(base_path, "icon.ico"))
        for path in icon_paths:
            if os.path.exists(path):
                try:
                    self.setWindowIcon(QIcon(path))
                    break
                except:
                    continue

    # ======= UI Initialization =======
    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 10, 20, 20) 
        main_layout.setSpacing(15)

        self._create_key_display(main_layout)
        self._create_button_area(main_layout)
        self._create_status_label(main_layout)

    def _create_key_display(self, parent_layout):
        self._create_key_section(parent_layout, self.strings["LBL_PRIVATE"], self.strings["HINT_PRIVATE"],
                                 self.strings["PLACEHOLDER_PRIVATE"], True)
        self._create_key_section(parent_layout, self.strings["LBL_PUBLIC"], self.strings["HINT_PUBLIC"],
                                 self.strings["PLACEHOLDER_PUBLIC"], False)

    def _create_key_section(self, parent_layout, title, hint, placeholder, is_private=False):
        layout = QVBoxLayout()
        row = QHBoxLayout()
        title_label = QLabel(title)     
        row.addWidget(title_label)
        hint_label = QLabel(hint)
        hint_label.setObjectName("HintLabel")
        row.addWidget(hint_label)
        row.addStretch()
        
        # Copy Button
        copy_btn = QPushButton(self.strings["BTN_COPY"])
        copy_btn.setObjectName("SecondaryButton")
        copy_btn.clicked.connect(lambda: self._copy_key(is_private))
        row.addWidget(copy_btn)
        
        # Save Button
        save_btn = QPushButton(self.strings["BTN_SAVE"])
        save_btn.setObjectName("SecondaryButton")
        save_btn.clicked.connect(lambda: self._save_key(is_private))
        row.addWidget(save_btn)
        
        layout.addLayout(row)
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText(placeholder)
        text_edit.setReadOnly(True)
        text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        
        if is_private:
            self.private_key_edit = text_edit
            layout.setStretchFactor(text_edit, 1) 
        else:
            self.public_key_edit = text_edit
            layout.setStretchFactor(text_edit, 1) 
            
        layout.addWidget(text_edit)
        parent_layout.addLayout(layout)

    def _create_button_area(self, parent_layout):
        layout = QHBoxLayout()
        layout.addStretch()
        self.generate_btn = QPushButton(self.strings["BTN_GENERATE"])
        self.generate_btn.setObjectName("PrimaryButton")
        self.generate_btn.clicked.connect(self._start_key_generation)
        layout.addWidget(self.generate_btn)
        layout.addStretch()
        parent_layout.addLayout(layout)

    def _create_status_label(self, parent_layout):
        self.status_label = QLabel(self.strings["STATUS_READY"])
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        parent_layout.addWidget(self.status_label)
        parent_layout.setStretchFactor(self.status_label, 0)

    # ======= Events/Async =======
    def _start_key_generation(self):
        self.generate_btn.setEnabled(False)
        self.status_label.setText(self.strings["STATUS_GENERATING"])
        self._set_text_with_color(self.private_key_edit, "PLACEHOLDER_PRIVATE")
        self._set_text_with_color(self.public_key_edit, "PLACEHOLDER_PUBLIC")
        
        self.generation_thread = QThread()
        self.worker = KeyGenerationWorker(self.age_keygen_path, self.strings)
        self.worker.moveToThread(self.generation_thread)
        
        # Connect signals
        self.worker.progress.connect(self._on_generation_progress)
        self.worker.finished.connect(self._on_generation_finished)
        self.worker.error.connect(self._on_generation_error)
        self.generation_thread.started.connect(self.worker.run)
        
        # Clean up thread and worker when done
        self.worker.finished.connect(self.generation_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.generation_thread.finished.connect(self.generation_thread.deleteLater)
        
        self.generation_thread.start()

    def _on_generation_progress(self, message):
        self.status_label.setText(message)
        QApplication.processEvents()

    def _on_generation_finished(self, private_key, public_key, error):
        if error:
            self._on_generation_error(error)
            return
        self._set_text_with_color(self.private_key_edit, private_key)
        self._set_text_with_color(self.public_key_edit, public_key)
        self.status_label.setText(self.strings["STATUS_SUCCESS"])
        self.generate_btn.setEnabled(True)

    def _on_generation_error(self, error_message):
        self.status_label.setText(self.strings["STATUS_ERROR"])
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, self.strings["ERROR_TITLE"], f"{error_message}")

    def _set_text_with_color(self, text_edit, text_key):
        text_edit.setReadOnly(False)
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.removeSelectedText()
        fmt = QTextCharFormat()
        
        if text_key in ["PLACEHOLDER_PRIVATE", "PLACEHOLDER_PUBLIC"]:
             fmt.setForeground(QColor(self.colors['TEXT_SECONDARY']))
        else:
             fmt.setForeground(QColor(self.colors['TEXT_PRIMARY']))
             
        cursor.setCharFormat(fmt)
        if text_key in self.strings:
            cursor.insertText(self.strings[text_key])
        else:
            cursor.insertText(text_key)
        text_edit.setTextCursor(cursor)
        text_edit.setReadOnly(True)

    def _copy_key(self, is_private):     
        key = (self.private_key_edit.toPlainText() if is_private else self.public_key_edit.toPlainText()).strip()
        placeholder_key = self.strings["PLACEHOLDER_PRIVATE"].strip() if is_private else self.strings["PLACEHOLDER_PUBLIC"].strip()
       
        if not key or key == placeholder_key:
            QMessageBox.warning(self, self.strings["WARNING_TITLE"], self.strings["MSG_NO_KEY"])
            return
            
        QGuiApplication.clipboard().setText(key)
        self.status_label.setText(self.strings["MSG_COPY_SUCCESS"])

    def _save_key(self, is_private):
      
        key = (self.private_key_edit.toPlainText() if is_private else self.public_key_edit.toPlainText()).strip()
        
        placeholder_key = self.strings["PLACEHOLDER_PRIVATE"].strip() if is_private else self.strings["PLACEHOLDER_PUBLIC"].strip()

      
        if not key or key == placeholder_key:
            QMessageBox.warning(self, self.strings["WARNING_TITLE"], self.strings["MSG_NO_KEY"])
            return
            
        default_ext = ".key" if is_private else ".txt"
        default_name = f"age_{'private' if is_private else 'public'}{default_ext}"
        
        file_filter = f"Age Private Key (*.key);;Text Files (*.txt);;All Files (*)" if is_private else f"Age Public Key (*.txt);;All Files (*)"

        path, _ = QFileDialog.getSaveFileName(self, self.strings["BTN_SAVE"], default_name, file_filter)
        
        if path:
            is_posix = os.name == "posix"
            
            if is_private and not path.lower().endswith(".key"):
                 path += ".key"
            
            try:
              
                with open(path, "w", encoding="utf-8") as f:
                    f.write(key)
                
                # Set permissions for private key on POSIX systems
                if is_posix and is_private:
                    os.chmod(path, 0o600) 
                    
                self.status_label.setText(self.strings["MSG_SAVE_SUCCESS"])
            except Exception as e:
                # Note: Changed error message to English
                QMessageBox.critical(self, self.strings["ERROR_TITLE"], f"Save failed: {str(e)}")


    def _apply_theme(self):
        self.setStyleSheet(ThemeManager.get_stylesheet())

    def _connect_signals(self):
        pass

# ==========================================
# 🏁 Main Program Execution
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AgeKeyGeneratorWindow()    
 
    # Windows Dark Mode Fix (Remains in Python for system integration)
    if platform.system() == "Windows":
        try:
            from ctypes import windll        
            HWND = windll.user32.GetParent(window.winId().__int__())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Constant for dark mode attribute
            
            # 1 to enable dark mode, 0 to disable
            if darkdetect.isDark():
                 windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_USE_IMMERSIVE_DARK_MODE, 1)
            else:
                 windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_USE_IMMERSIVE_DARK_MODE, 0)
        except Exception:
            # Silence dark mode setting errors
            pass 

    window.show()
    sys.exit(app.exec())