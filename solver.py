import sys
import requests
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QTextEdit, QPushButton, QComboBox, 
                            QHBoxLayout, QLineEdit, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt

from PyQt6.QtGui import QTextCursor

from threads import OllamaThread, OllamaDownloadThread

class OllamaMathSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_models()
        
    def setup_ui(self):
        """Set up the user interface components"""
        self.setWindowTitle("Ollama Math Solver")
        self.setMinimumSize(700, 500)
        
        # Create main layout with splitter
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Input section
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Model selection (horizontal layout)
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        
        self.model_box = QComboBox()
        self.model_box.setEditable(True)
        model_row.addWidget(self.model_box)
        
        # Download button
        download_btn = QPushButton("Download")
        download_btn.clicked.connect(self.download_model)
        model_row.addWidget(download_btn)
        input_layout.addLayout(model_row)

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_model)
        model_row.addWidget(delete_btn)

        
        # Problem input
        input_layout.addWidget(QLabel("Math Problem:"))
        self.problem_box = QTextEdit()
        self.problem_box.setPlaceholderText("Enter your math problem here...")
        input_layout.addWidget(self.problem_box)
        
        # System prompt 
        prompt_row = QHBoxLayout()
        prompt_row.addWidget(QLabel("System Prompt:"))
        self.prompt_field = QLineEdit("You are a helpful math assistant. Solve the given problem step by step.")
        prompt_row.addWidget(self.prompt_field)
        input_layout.addLayout(prompt_row)
        
        # Solve button
        solve_btn = QPushButton("Solve Problem")
        solve_btn.clicked.connect(self.solve_problem)
        input_layout.addWidget(solve_btn)
        
        # Output section
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        output_layout.addWidget(QLabel("Solution:"))
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        output_layout.addWidget(self.output_box)
        
        # Add both sections to splitter
        splitter.addWidget(input_widget)
        splitter.addWidget(output_widget)
        splitter.setSizes([250, 250])
        
        # Status bar for feedback
        self.statusBar().showMessage("Ready")
    
    def load_models(self):
        """Load available models from Ollama"""
        self.statusBar().showMessage("Loading models...")
        
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # Save current selection
                current = self.model_box.currentText()
                
                # Update model list
                self.model_box.clear()
                for model in models:
                    self.model_box.addItem(model["name"])
                
                # Restore selection if possible
                if current and self.model_box.findText(current) >= 0:
                    self.model_box.setCurrentText(current)
                    
                self.statusBar().showMessage(f"Loaded {len(models)} models")
            else:
                self.statusBar().showMessage("Failed to load models")
                QMessageBox.warning(self, "Error", f"Failed to fetch models: {response.status_code}")
        except Exception as e:
            self.statusBar().showMessage("Connection error")
            QMessageBox.warning(self, "Connection Error", 
                               f"Could not connect to Ollama. Make sure it's running.\n\nError: {str(e)}")
    
    def solve_problem(self):
        """Process the math problem using Ollama"""
        problem = self.problem_box.toPlainText().strip()
        if not problem:
            QMessageBox.warning(self, "Error", "Please enter a math problem.")
            return
        
        model = self.model_box.currentText().strip()
        if not model:
            QMessageBox.warning(self, "Error", "Please select a model.")
            return
        
        # Show processing state
        self.output_box.clear()
        self.statusBar().showMessage(f"Processing with model: {model}")
        
        # Process in background thread
        self.solver_thread = OllamaThread(model, problem, self.prompt_field.text())
        self.solver_thread.token_received.connect(self.append_token)
        self.solver_thread.error_occurred.connect(self.show_error)
        self.solver_thread.finished.connect(lambda: self.statusBar().showMessage("Ready"))
        self.solver_thread.start()
    
    def append_token(self, token):
        self.output_box.moveCursor(QTextCursor.MoveOperation.End)
        self.output_box.insertPlainText(token)
        self.output_box.ensureCursorVisible()


    def display_solution(self, solution):
        """Display the solution from Ollama"""
        self.output_box.setText(solution)
    
    def show_error(self, message):
        """Display error messages"""
        self.output_box.setText(message)
        QMessageBox.warning(self, "Error", message)

    def download_model(self):
        """Download a model from Ollama"""
        model_name = self.model_box.currentText().strip()
        if not model_name:
            QMessageBox.warning(self, "Error", "Please enter a model name to download.")
            return

        self.statusBar().showMessage(f"Downloading model: {model_name}")
        self.output_box.append(f"Starting download of model: {model_name}")

        self.download_thread = OllamaDownloadThread(model_name)
        self.download_thread.progress.connect(self.update_download_progress)
        self.download_thread.error.connect(lambda msg: QMessageBox.warning(self, "Download Error", msg))
        self.download_thread.done.connect(lambda: self.statusBar().showMessage(f"Download complete: {model_name}"))
        self.download_thread.done.connect(lambda: self.output_box.append(f"Download complete"))
        self.download_thread.done.connect(self.load_models)
        self.download_thread.start()

    def update_download_progress(self, percent_str):
        """Update the output box with just the current download percentage"""
        cursor = self.output_box.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.removeSelectedText()
        cursor.insertText(f"Downloading: {percent_str}")

    def delete_model(self):
        """Delete the selected model"""
        model_name = self.model_box.currentText().strip()
        if not model_name:
            QMessageBox.warning(self, "Error", "Please select a model to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the model '{model_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete("http://localhost:11434/api/delete", json={"name": model_name})
                if response.status_code == 200:
                    self.statusBar().showMessage(f"Deleted model: {model_name}")
                    self.output_box.append(f"Deleted model: {model_name}")
                    self.load_models()
                else:
                    QMessageBox.warning(self, "Delete Failed", f"Error deleting model:\n{response.text}")
            except Exception as e:
                QMessageBox.warning(self, "Connection Error", f"Could not connect to Ollama.\n\nError: {str(e)}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OllamaMathSolver()
    window.show()
    sys.exit(app.exec())