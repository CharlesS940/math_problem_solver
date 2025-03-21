import sys
import subprocess
import threading
import ollama
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QLabel, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, QObject

MODEL_NAME = "deepseek-r1:7b"

class SignalEmitter(QObject):
    update_output = pyqtSignal(str)

class MathSolverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = SignalEmitter()
        self.signals.update_output.connect(self.handle_output_update)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Math Solver")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        # Input box
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Enter a math problem...")
        self.input_box.setFixedHeight(80)
        layout.addWidget(self.input_box)

        # Solve button
        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve_math_problem)
        layout.addWidget(self.solve_button)

        # Scrollable output box
        self.output_area = QScrollArea()
        self.output_label = QLabel("Solution will appear here.")
        self.output_label.setWordWrap(True)
        self.output_label.setFixedWidth(550)

        self.output_area.setWidgetResizable(True)
        self.output_area.setWidget(self.output_label)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def solve_math_problem(self):
        problem = self.input_box.toPlainText().strip()
        if not problem:
            self.output_label.setText("❌ Please enter a math problem.")
            return

        self.output_label.setText("⏳ Solving... Please wait...")

        # Run the inference in a separate thread
        thread = threading.Thread(target=self.run_inference, args=(problem,))
        thread.start()

    def run_inference(self, problem):
        print("🔍 Starting inference thread...")

        if not self.is_ollama_running():
            print("⚠️ Ollama is not running.")
            self.signals.update_output.emit("⚠️ Ollama server is not running. Please start it with 'ollama serve'.")
            return

        print("📥 Pulling model...")
        self.pull_model()
        print("✅ Model pulled.")

        llm_prompt = f"""You are a helpful math tutor. A student asks you to solve the following math problem.
You should give both the numerical answer and the explanation.

Problem: {problem}
"""

        try:
            print("🤖 Sending prompt to Ollama...")
            llm_response = ollama.generate(model=MODEL_NAME, prompt=llm_prompt, options={"num_predict": 1000})
            print("✅ Response received from Ollama.")
            response_text = llm_response["response"].strip()
            full_output = f"📝 {response_text}"
            self.signals.update_output.emit(full_output)
        except Exception as e:
            print(f"❌ Exception during inference: {str(e)}")
            self.signals.update_output.emit(f"❌ Error during inference: {str(e)}")

    def is_ollama_running(self):
        try:
            subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def pull_model(self):
        subprocess.run(["ollama", "pull", MODEL_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def handle_output_update(self, text):
        print(f"🖥️ Updating UI with response (first 100 chars): {text[:100]}...")
        self.output_label.setText(text)

if __name__ == "__main__":
    print("🚀 Starting Math Solver App...")
    app = QApplication(sys.argv)
    solver = MathSolverApp()
    solver.show()
    print("📢 App launched successfully.")
    sys.exit(app.exec())
