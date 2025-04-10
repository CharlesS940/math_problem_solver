# Ollama math assistant

Hello and welcome to my repository!

I am implementing a desktop application that provides explanations for math problems using locally run LLMs with Ollama.

Below you will find requirements and a guide on how to use the app.

# Setup

The required python version is 3.10.

I am using poetry to manage packages so you will need to install it if you do not have it already:

'''
curl -sSL https://install.python-poetry.org | python3 -
'''

and in the cloned repository: 

'''
poetry install
'''

to install poetry and the virtual envorinment specified in pyproject.toml.

Ollama is also required to run this application, you can find download instructions here: https://ollama.com/download.

# Run

To run the application you will first need to open a terminal and run:

'''
ollama serve
'''

to start the ollama server. 

Then open up a new terminal, navigate to the cloned repository and run:

'''
poetry run python solver.py
'''

which will open the PyQt widget and start the application!

# Features

