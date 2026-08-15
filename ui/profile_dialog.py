"""
LagForge - Custom Profile Presets Dialog (v1.101)
Obsidian modal dialog for managing and loading custom delay & packet loss profiles.
"""

from typing import Dict, Any, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from .styles import COLORS


class ProfileManagerDialog(QDialog):
    """
    Modal dialog allowing users to save current settings as named profiles,
    select from saved profiles, and delete obsolete profiles.
    """

    profile_selected = Signal(dict)

    def __init__(
        self,
        current_settings: Dict[str, Any],
        saved_profiles: List[Dict[str, Any]],
        parent: QWidget = None
    ):
        super().__init__(parent)
        self.current_settings = current_settings
        self.profiles = saved_profiles.copy()

        self.setWindowTitle("LagForge Profiles")
        self.setFixedSize(380, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._init_ui()
        self._populate_list()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        lbl_title = QLabel("Profile Presets Manager")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel("Save or activate customized latency profiles:")
        lbl_desc.setStyleSheet("font-size: 12px; color: #9CA3AF;")
        layout.addWidget(lbl_desc)

        # Profiles List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: #12141F;
                border: 1px solid {COLORS['card_border']};
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-radius: 6px;
            }}
            QListWidget::item:hover {{
                background-color: #1A1F30;
                color: {COLORS['accent_cyan']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['preset_active_bg']};
                color: {COLORS['accent_cyan']};
                border: 1px solid {COLORS['accent_cyan']};
            }}
        """)
        layout.addWidget(self.list_widget)

        # Save Current Settings Box
        save_layout = QHBoxLayout()
        save_layout.setSpacing(8)

        self.txt_profile_name = QLineEdit()
        self.txt_profile_name.setPlaceholderText("New profile name...")
        self.txt_profile_name.setStyleSheet(f"""
            QLineEdit {{
                background-color: #151824;
                border: 1px solid {COLORS['card_border']};
                border-radius: 8px;
                padding: 8px 10px;
                color: #FFFFFF;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['accent_cyan']};
            }}
        """)
        save_layout.addWidget(self.txt_profile_name)

        btn_save = QPushButton("Save Current")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: #161A28;
                border: 1px solid {COLORS['accent_cyan']};
                border-radius: 8px;
                color: {COLORS['accent_cyan']};
                font-size: 12px;
                font-weight: 700;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background-color: #0E2A3C;
            }}
        """)
        btn_save.clicked.connect(self._on_save_clicked)
        save_layout.addWidget(btn_save)

        layout.addLayout(save_layout)

        # Action Buttons (Load / Delete / Close)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        btn_delete = QPushButton("Delete")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: #1E161C;
                border: 1px solid #5A212D;
                border-radius: 8px;
                color: #F43F5E;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: #36151E;
            }}
        """)
        btn_delete.clicked.connect(self._on_delete_clicked)
        actions_layout.addWidget(btn_delete)

        actions_layout.addStretch()

        btn_load = QPushButton("Apply Profile")
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.setStyleSheet(f"""
            QPushButton {{
                background-color: #00B4D8;
                border: 1px solid {COLORS['accent_cyan']};
                border-radius: 8px;
                color: #031620;
                font-size: 12px;
                font-weight: 800;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #00D2F0;
            }}
        """)
        btn_load.clicked.connect(self._on_load_clicked)
        actions_layout.addWidget(btn_load)

        layout.addLayout(actions_layout)

    def _populate_list(self):
        self.list_widget.clear()
        for p in self.profiles:
            item_text = f"{p['name']}  (+{p.get('ping', 0)}ms, ±{p.get('jitter', 0)}ms, {p.get('loss', 0)}% loss)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, p)
            self.list_widget.addItem(item)

    def _on_save_clicked(self):
        name = self.txt_profile_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Profile Name Required", "Please enter a profile name.")
            return

        new_profile = {
            "name": name,
            "ping": int(self.current_settings.get("ping", 325)),
            "jitter": float(self.current_settings.get("jitter", 0.0)),
            "loss": float(self.current_settings.get("loss", 0.0)),
        }

        # Replace existing or append
        existing_idx = next((i for i, p in enumerate(self.profiles) if p["name"].lower() == name.lower()), -1)
        if existing_idx >= 0:
            self.profiles[existing_idx] = new_profile
        else:
            self.profiles.append(new_profile)

        self.txt_profile_name.clear()
        self._populate_list()

    def _on_delete_clicked(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            del self.profiles[current_row]
            self._populate_list()

    def _on_load_clicked(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.information(self, "Select Profile", "Please select a profile to apply.")
            return

        profile_data = current_item.data(Qt.UserRole)
        self.profile_selected.emit(profile_data)
        self.accept()
