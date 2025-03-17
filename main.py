import sys
import subprocess
import ollama
import sympy as sp
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea

MODEL_NAME = "deepseek-r1:7b"  # Use "deepseek-r1:7b" if preferred

class MathSolverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Math Solver")
        self.setGeometry(200, 200, 600, 400)  # Increased window size

        layout = QVBoxLayout()

        # Input box for user question
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Enter a math problem...")
        self.input_box.setFixedHeight(80)  # Larger input box
        layout.addWidget(self.input_box)

        # Solve button
        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve_math_problem)
        layout.addWidget(self.solve_button)

        # Scrollable output box
        self.output_area = QScrollArea()
        self.output_label = QLabel("Solution will appear here.")
        self.output_label.setWordWrap(True)
        self.output_label.setFixedWidth(550)  # Adjust width for readability

        self.output_area.setWidgetResizable(True)
        self.output_area.setWidget(self.output_label)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def solve_math_problem(self):
        problem = self.input_box.toPlainText().strip()
        if not problem:
            self.output_label.setText("❌ Please enter a math problem.")
            return

        # Ensure Ollama is running
        if not self.is_ollama_running():
            self.output_label.setText("⏳ Starting Ollama server...")
            self.start_ollama()

        # Ensure the model is available
        self.pull_model()

        # Step 1: Ask the LLM to interpret the problem
        llm_prompt = f"""You are a helpful math tutor. A student asks you to solve the following math problem.
        You should give both the numerical answer and the explanation

        Problem: {problem}
        """

        llm_response = ollama.generate(model=MODEL_NAME, prompt=llm_prompt, options={"num_predict": 1000})
        response_text = llm_response["response"].strip()

        # Display the explanation + solution
        full_output = f"📝 {response_text}"
        self.output_label.setText(full_output)


    def is_ollama_running(self):
        """Check if Ollama is running by executing 'ollama list'."""
        try:
            subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def start_ollama(self):
        """Start Ollama in the background if it's not already running."""
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def pull_model(self):
        """Ensure the model is available."""
        print(f"📥 Pulling model '{MODEL_NAME}' if not available...")
        subprocess.run(["ollama", "pull", MODEL_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Model '{MODEL_NAME}' is ready.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    solver = MathSolverApp()
    solver.show()
    sys.exit(app.exec())
