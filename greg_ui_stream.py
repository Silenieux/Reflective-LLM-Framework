# Unified Reflective Assistant GUI with Streaming Support
# Combines PySide6 GUI with streaming LLM responses and complete memory functionality

import sys
import time
from pathlib import Path

# Allow modular imports from project root
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

import os
import sqlite3
import numpy as np
import faiss
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QTableView, QHeaderView, QHBoxLayout, QAbstractItemView, QTextEdit,
    QLabel, QCheckBox, QTabWidget, QProgressBar
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PySide6.QtCore import Qt, QThread, Signal
from sentence_transformers import SentenceTransformer
from importlib import reload

# Import core logic with fallback mocks for standalone operation
try:
    from core.faiss_core import vector_search
    from core.llm.llm_interface import query_llm
    from core.greg_routes import (
        fallback_translate_llm_output,
        detect_self_emotion_check, detect_sentience_prompt,
        generate_sentience_reflection, inject_apology,
        detect_absurdity,
        route_query
    )
    from core.utils.web_tools import *
    import ext_modules.prompt_clinic as prompt_clinic
    from reflective_agent_core.tone_interpreter import interpret_tone
    MODULES_AVAILABLE = True
except ImportError:
    # Fallback mocks for standalone demonstration
    def vector_search(*args, **kwargs): return []
    def query_llm(*args, **kwargs): return "Mock LLM response"
    def detect_self_emotion_check(prompt): return False
    def detect_sentience_prompt(prompt): return False
    def generate_sentience_reflection(): return "This is a reflection on sentience."
    def fallback_translate_llm_output(response, query): return response
    def interpret_tone(text): return "neutral", "neutral"
    def route_query(query, **kwargs):
        # Mock streaming generator
        response = f"Mock response to: {query}"
        for char in response:
            time.sleep(0.01)  # Simulate streaming delay
            yield char
    
    class MockPromptClinic:
        @staticmethod
        def analyze_prompt(query): return {"analysis": "Mock analysis"}
        @staticmethod
        def improve_prompt(query): return f"Improved: {query}"
    
    prompt_clinic = MockPromptClinic()
    MODULES_AVAILABLE = False

# Constants
MEMORY_DIR = PROJECT_ROOT / "memory"
DB_PATH = MEMORY_DIR / "reflective_memory.db"
INDEX_PATH = MEMORY_DIR / "reflective_memory.index"

class QueryWorker(QThread):
    """Worker thread for streaming LLM responses"""
    token_received = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, query, kwargs):
        super().__init__()
        self.query = query
        self.kwargs = kwargs
        self._is_running = True

    def run(self):
        """Execute the query in a separate thread with streaming support"""
        try:
            full_response = ""
            
            # Check if route_query returns a generator (streaming) or string
            result = route_query(self.query, **self.kwargs)
            
            if hasattr(result, '__iter__') and not isinstance(result, str):
                # Streaming response
                for token in result:
                    if not self._is_running:
                        break
                    self.token_received.emit(token)
                    full_response += token
            else:
                # Non-streaming response
                full_response = str(result)
                self.token_received.emit(full_response)
            
            if self._is_running:
                self.finished.emit(full_response)
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        self._is_running = False

class UnifiedAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Greg - Unified Streaming Interface")
        self.resize(1200, 700)
        self.query_worker = None
        self.full_response = ""

        # Initialize sentence transformer
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        except Exception as e:
            print(f"Failed to load SentenceTransformer model: {e}")
            self.embedder = None

        # Ensure memory directory exists
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.init_database()

        # Setup UI
        self.tabs = QTabWidget()
        self.setup_prompt_tab()
        self.setup_memory_tab()

        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addWidget(self.tabs)
        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self.load_memory()

    def init_database(self):
        """Initialize the SQLite database and FAISS index if they don't exist"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS reflective_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT,
                reflective_prompt TEXT,
                tone_before TEXT,
                tone_after TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS tone_rules (
                tone_before TEXT,
                tone_after TEXT,
                severity INTEGER,
                should_escalate BOOLEAN
            )''')
            
            conn.commit()
            conn.close()
            
            # Initialize FAISS index if it doesn't exist
            if not INDEX_PATH.exists() and self.embedder:
                index = faiss.IndexFlatIP(384)  # MiniLM embedding dimension
                faiss.write_index(index, str(INDEX_PATH))
                
        except Exception as e:
            print(f"Database initialization error: {e}")

    def setup_prompt_tab(self):
        """Setup the main prompt and response interface"""
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt here... (Press Enter to submit, Shift+Enter for new line)")
        self.prompt_input.keyPressEvent = self.handle_key_press

        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setPlaceholderText("Greg's response will stream here...")

        self.submit_button = QPushButton("Submit Prompt")
        self.submit_button.clicked.connect(self.handle_submit)
        
        self.stop_button = QPushButton("Stop Generation")
        self.stop_button.clicked.connect(self.stop_generation)
        self.stop_button.setEnabled(False)
        
        self.thinking_indicator = QLabel("Greg is thinking...")
        self.thinking_indicator.setAlignment(Qt.AlignCenter)
        self.thinking_indicator.setVisible(False)

        # Controls
        self.llm_toggle = QCheckBox("Use LLM")
        self.llm_toggle.setChecked(True)
        self.greg_mode = QCheckBox("Call Me Greg")
        self.auto_save = QCheckBox("Auto-Save Reflections")
        self.auto_save.setChecked(True)
        self.use_web = QCheckBox("Enable Internet Access")
        self.use_prompt_clinic = QCheckBox("Enable Prompt Clinic")
        
        clinic_button = QPushButton("Run Prompt Clinic")
        clinic_button.clicked.connect(self.run_prompt_clinic)

        # Layout
        prompt_layout = QVBoxLayout()
        prompt_layout.addWidget(QLabel("Prompt Input:"))
        prompt_layout.addWidget(self.prompt_input)

        button_row = QHBoxLayout()
        button_row.addWidget(self.submit_button)
        button_row.addWidget(self.stop_button)
        button_row.addWidget(clinic_button)
        prompt_layout.addLayout(button_row)
        
        prompt_layout.addWidget(self.thinking_indicator)
        prompt_layout.addWidget(QLabel("Response:"))
        prompt_layout.addWidget(self.response_output)

        controls_row = QHBoxLayout()
        for widget in [self.llm_toggle, self.auto_save, self.greg_mode, self.use_web, self.use_prompt_clinic]:
            controls_row.addWidget(widget)
        prompt_layout.addLayout(controls_row)

        tab1 = QWidget()
        tab1.setLayout(prompt_layout)
        self.tabs.addTab(tab1, "Prompt & Response")

    def setup_memory_tab(self):
        """Setup the memory management interface"""
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Cue", "Reflection", "Tone Before", "Tone After", "Severity", "Risk"
        ])

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Memory controls
        reload_button = QPushButton("Reload Memory")
        reload_button.clicked.connect(self.load_memory)

        delete_button = QPushButton("Delete Selected")
        delete_button.setStyleSheet("background-color: pink")
        delete_button.clicked.connect(self.delete_selected)

        refresh_modules_button = QPushButton("🔄 Refresh Modules")
        refresh_modules_button.clicked.connect(self.reload_modules)

        memory_layout = QVBoxLayout()
        memory_layout.addWidget(self.table)

        memory_controls = QHBoxLayout()
        for widget in [reload_button, delete_button, refresh_modules_button]:
            memory_controls.addWidget(widget)
        memory_layout.addLayout(memory_controls)

        tab2 = QWidget()
        tab2.setLayout(memory_layout)
        self.tabs.addTab(tab2, "Memory")

    def handle_key_press(self, event):
        """Handle keyboard shortcuts in prompt input"""
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self.handle_submit()
        else:
            QTextEdit.keyPressEvent(self.prompt_input, event)

    def handle_submit(self):
        """Handle prompt submission with streaming support"""
        if self.query_worker and self.query_worker.isRunning():
            return

        query = self.prompt_input.toPlainText().strip()
        if not query:
            return

        self.response_output.clear()
        self.full_response = ""
        self.submit_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.thinking_indicator.setVisible(True)

        # Handle special cases synchronously
        if detect_self_emotion_check(query) or detect_sentience_prompt(query):
            self.full_response = generate_sentience_reflection()
            self.response_output.setPlainText(f"[TONE: neutral → philosophical]\n{self.full_response}")
            self.query_finished()
            return

        # Start background worker for LLM query
        kwargs = {
            'tone': 'neutral',
            'internet_enabled': self.use_web.isChecked()
        }
        
        self.query_worker = QueryWorker(query, kwargs)
        self.query_worker.token_received.connect(self.append_token)
        self.query_worker.finished.connect(self.query_finished)
        self.query_worker.error.connect(self.query_error)
        self.query_worker.start()

    def stop_generation(self):
        """Stop the current generation"""
        if self.query_worker and self.query_worker.isRunning():
            self.query_worker.stop()
            self.query_worker.wait()
        self.query_finished()

    def append_token(self, token):
        """Append streaming token to the response"""
        if self.thinking_indicator.isVisible():
            self.thinking_indicator.setVisible(False)
        
        cursor = self.response_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(token)
        self.response_output.setTextCursor(cursor)
        self.full_response += token

    def query_finished(self):
        """Handle query completion"""
        # Post-process the response
        query = self.prompt_input.toPlainText().strip()
        processed_response = fallback_translate_llm_output(self.full_response, query)
        
        # Determine tones
        tone_b, tone_a = interpret_tone(query)
        if "I'm sorry" in processed_response or "apologize" in processed_response:
            tone_a = "apologetic"
        
        # Update UI with tone information
        self.response_output.append(f"\n\n[TONE: {tone_b} → {tone_a}]")

        # Auto-save if enabled
        if self.auto_save.isChecked():
            self.save_memory(query, processed_response, tone_b, tone_a)
            self.load_memory()  # Refresh memory table

        # Reset UI state
        self.submit_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.thinking_indicator.setVisible(False)

    def query_error(self, error_message):
        """Handle query errors"""
        self.response_output.append(f"\n\n[ERROR]: {error_message}")
        self.submit_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.thinking_indicator.setVisible(False)

    def run_prompt_clinic(self):
        """Run prompt clinic analysis"""
        try:
            if not self.use_prompt_clinic.isChecked():
                self.response_output.setPlainText("[Prompt Clinic] Feature disabled. Enable it first.")
                return
                
            query = self.prompt_input.toPlainText().strip()
            if not query:
                self.response_output.setPlainText("[Prompt Clinic] Empty prompt. Try typing something.")
                return

            diagnosis = prompt_clinic.analyze_prompt(query)
            improved = prompt_clinic.improve_prompt(query)

            diag_text = "\n".join([f"- {k}: {v}" for k, v in diagnosis.items()]) if diagnosis else "Looks solid."
            final_text = f"[PROMPT CLINIC]\n--- Diagnosis ---\n{diag_text}\n\n--- Suggested Revision ---\n{improved}"
            self.response_output.setPlainText(final_text)
            
        except Exception as e:
            self.response_output.setPlainText(f"[Prompt Clinic Error] {str(e)}")

    def load_memory(self):
        """Load memory entries into the table"""
        self.model.removeRows(0, self.model.rowCount())
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, summary, reflective_prompt, tone_before, tone_after 
                FROM reflective_memory 
                ORDER BY id DESC
            """)
            
            for row in cursor.fetchall():
                meta = self.get_tone_meta(row[3], row[4])
                items = [
                    QStandardItem(str(row[0])),
                    QStandardItem(row[1][:50] + "..." if len(row[1]) > 50 else row[1]),
                    QStandardItem(row[2][:100] + "..." if len(row[2]) > 100 else row[2]),
                    QStandardItem(row[3]),
                    QStandardItem(row[4]),
                    QStandardItem(str(meta['severity'])),
                    QStandardItem("⚠️" if meta['should_escalate'] else "")
                ]
                self.model.appendRow(items)
            conn.close()
            
        except Exception as e:
            print(f"Error loading memory: {e}")

    def get_tone_meta(self, before, after):
        """Get tone metadata from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT severity, should_escalate 
                FROM tone_rules 
                WHERE tone_before=? AND tone_after=?
            """, (before, after))
            result = cursor.fetchone()
            conn.close()
            
            return {
                "severity": result[0] if result else 0,
                "should_escalate": bool(result[1]) if result else False
            }
        except:
            return {"severity": 0, "should_escalate": False}

    def delete_selected(self):
        """Delete selected memory entries"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
            
        ids = [int(self.model.item(row.row(), 0).text()) for row in selected]
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.executemany("DELETE FROM reflective_memory WHERE id = ?", [(i,) for i in ids])
            conn.commit()
            conn.close()
            self.load_memory()
        except Exception as e:
            print(f"Error deleting entries: {e}")

    def save_memory(self, summary, reflection, tone_b, tone_a):
        """Save memory entry to database and FAISS index"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reflective_memory (summary, reflective_prompt, tone_before, tone_after) 
                VALUES (?, ?, ?, ?)
            """, (summary, reflection, tone_b, tone_a))
            conn.commit()
            
            # Add to FAISS index if embedder is available
            if self.embedder and INDEX_PATH.exists():
                embedding = self.embedder.encode([summary]).astype("float32")
                index = faiss.read_index(str(INDEX_PATH))
                index.add_with_ids(embedding, np.array([cursor.lastrowid]))
                faiss.write_index(index, str(INDEX_PATH))
            
            conn.close()
            
        except Exception as e:
            print(f"Error saving memory: {e}")

    def reload_modules(self):
        """Reload core modules for development"""
        if not MODULES_AVAILABLE:
            print("Core modules not available - running in mock mode")
            return
            
        try:
            # Reload modules
            import reflective_agent_core.tone_interpreter as tone_interpreter_reload
            import core.greg_routes as greg_routes
            import core.llm.llm_interface as llm_interface
            import core.utils.web_tools as web_tools
            import ext_modules.prompt_clinic as prompt_clinic_reload
            
            reload(tone_interpreter_reload)
            reload(greg_routes)
            reload(llm_interface)
            reload(web_tools)
            reload(prompt_clinic_reload)

            # Update global references
            global route_query, query_llm, fallback_translate_llm_output, prompt_clinic, interpret_tone
            route_query = greg_routes.route_query
            fallback_translate_llm_output = greg_routes.fallback_translate_llm_output
            query_llm = llm_interface.query_llm
            prompt_clinic = prompt_clinic_reload
            interpret_tone = tone_interpreter_reload.interpret_tone

            print("Modules reloaded successfully")
            
        except Exception as e:
            print(f"Error reloading modules: {e}")

def main():
    app = QApplication(sys.argv)
    window = UnifiedAssistantGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()