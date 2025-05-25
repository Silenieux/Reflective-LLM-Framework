from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QMenuBar, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QTextEdit, QPushButton
)
from PySide6.QtGui import QAction
from PySide6.QtCore import QTimer

from sqlite_store import fetch_all_entries
from llm_runner import generate_response

import sys
import os

class SymbolicAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symbolic Assistant")
        self.resize(1000, 700)

        self.init_menu()
        self.init_ui()

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        reload_action = QAction("Reload Memory", self)
        reload_action.triggered.connect(self.reload_memory)
        file_menu.addAction(reload_action)

        restart_action = QAction("Restart App", self)
        restart_action.triggered.connect(self.restart_app)
        file_menu.addAction(restart_action)

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        self.memory_table = QTableWidget()
        self.memory_table.setColumnCount(5)
        self.memory_table.setHorizontalHeaderLabels([
            "Title", "Summary", "Tone (before→after)", "Bias Tags", "Cue"
        ])
        self.memory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter customer message here...")

        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setPlaceholderText("LLM response will appear here...")

        self.run_button = QPushButton("Generate Response")
        self.run_button.clicked.connect(self.run_prompt_test)

        layout.addWidget(self.user_input)
        layout.addWidget(self.run_button)
        layout.addWidget(self.response_output)
        layout.addWidget(self.memory_table)
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.load_memory_entries()

    def load_memory_entries(self):
        entries = fetch_all_entries()
        self.memory_table.setRowCount(len(entries))

        for row_idx, (entry, embedding) in enumerate(entries):
            self.memory_table.setItem(row_idx, 0, QTableWidgetItem(entry.get("Title", "")))
            self.memory_table.setItem(row_idx, 1, QTableWidgetItem(entry.get("Summary", "")))
            tone = entry.get("tone_context", {})
            tone_str = f"{tone.get('before', '')} → {tone.get('after', '')}"
            self.memory_table.setItem(row_idx, 2, QTableWidgetItem(tone_str))
            self.memory_table.setItem(row_idx, 3, QTableWidgetItem(", ".join(entry.get("Bias Tags", []))))
            self.memory_table.setItem(row_idx, 4, QTableWidgetItem(entry.get("Continuity Cue", "")))

    def run_prompt_test(self):
        user_msg = self.user_input.text().strip()
        if not user_msg:
            self.response_output.setPlainText("[error] Please enter a customer message.")
            return

        selected_row = self.memory_table.currentRow()
        if selected_row == -1:
            self.response_output.setPlainText("[error] Please select a symbolic memory entry.")
            return

        # Build symbolic context block from selected row
        title = self.memory_table.item(selected_row, 0).text()
        summary = self.memory_table.item(selected_row, 1).text()
        tone = self.memory_table.item(selected_row, 2).text()
        tags = self.memory_table.item(selected_row, 3).text()
        cue = self.memory_table.item(selected_row, 4).text()

        context_block = (
            f"[TITLE={title}]\n"
            f"[SUMMARY={summary}]\n"
            f"[TONE_SHIFT={tone}]\n"
            f"[TAGS={tags}]\n"
            f"[CUE={cue}]"
        )

        # Call LLM
        self.response_output.setPlainText("[~] Generating response...")
        try:
            reply = generate_response(context_block, user_msg)
            self.response_output.setPlainText(reply)
        except Exception as e:
            self.response_output.setPlainText(f"[error] LLM failed: {e}")

    def reload_memory(self):
        self.load_memory_entries()

    def restart_app(self):
        print("[log] Restarting application...")
        QTimer.singleShot(500, self._do_restart)

    def _do_restart(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SymbolicAssistantGUI()
    window.show()
    sys.exit(app.exec())
