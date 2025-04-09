import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal

class OllamaThread(QThread):
    token_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, model, problem, system_prompt):
        super().__init__()
        self.model = model
        self.problem = problem
        self.system_prompt = system_prompt

    def run(self):
        try:
            request_data = {
                "model": self.model,
                "prompt": self.problem,
                "system": self.system_prompt,
                "stream": True
            }
            with requests.post("http://localhost:11434/api/generate", json=request_data, stream=True) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                token = data.get("response", "")
                                if token:
                                    self.token_received.emit(token)
                            except json.JSONDecodeError:
                                continue
                else:
                    self.error_occurred.emit(f"Error: {response.status_code}\n{response.text}")
        except Exception as e:
            self.error_occurred.emit(f"Failed to connect to Ollama API: {str(e)}")


class OllamaDownloadThread(QThread):
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def run(self):
        try:
            with requests.post("http://localhost:11434/api/pull", json={"name": self.model_name}, stream=True) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                completed = int(data.get("completed", 0))
                                total = int(data.get("total", 0))
                                if total > 0:
                                    percent = int((completed / total) * 100)
                                    self.progress.emit(f"{percent}%")
                            except (json.JSONDecodeError, ValueError, ZeroDivisionError):
                                continue
                    self.progress.emit("100%")
                    self.done.emit()
                else:
                    self.error.emit(f"Download failed: {response.status_code}\n{response.text}")
        except Exception as e:
            self.error.emit(str(e))