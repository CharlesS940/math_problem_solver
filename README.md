# Ollama math assistant

Hello and welcome to my repository!

I am implementing a desktop application that provides explanations for math problems using locally run LLMs with Ollama.

Below you will find requirements and a guide on how to use the app.

# Setup

The required python version is 3.10.

I am using poetry to manage packages so you will need to install it if you do not have it already:

```
# Linux
curl -sSL https://install.python-poetry.org | python3 -

# Mac-os
curl -sSL https://install.python-poetry.org | python3 -

# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

and in the cloned repository:

```
poetry install
```

to install poetry and the virtual environment specified in pyproject.toml.

Ollama is also required to run this application, you can find download instructions here: https://ollama.com/download.

# Run

To run the application you will first need to open a terminal and run:

```
ollama serve
```

to start the ollama server. 

Then open up a new terminal, navigate to the cloned repository and run:

```
poetry run python solver.py
```

which will open the PyQt widget and start the application!

# Downloading models from Ollama

Go to https://ollama.com/search and find the model you would like to use, RAM requirements are listed with the models so keep in mind your PC specs.

Type the model's name as it appears in Ollama and click download (eg: gemma2:2b for the 2 billion parameter version of gemma2). 

You will then be able to select it for inference in the drop down menu.

# Features

Streamed local LLM responses

Download models on demand via Ollama

Delete models to manage disk space

Designed for math-focused prompts — but works with any topic

Desktop interface with PyQt6

# Update plan

SymPy support to improve accuracy on numerical problems

GPU support
