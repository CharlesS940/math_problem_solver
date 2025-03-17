import shutil

def ensure_ollama_installed():
    """Ensure Ollama is installed system-wide."""
    ollama_path = shutil.which("ollama")

    if ollama_path:
        print(f"✅ Ollama found: {ollama_path}")
        return ollama_path
    
    else:
        print("🚫 Ollama not found. Please install Ollama and add to Path")

# Ensure Ollama is available before proceeding
ollama_path = ensure_ollama_installed()
