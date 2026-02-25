# rubbersoul

I don't like to write them, you don't like to write them, so f it let the llm do it.

## Requirements

* Python **3.11 or higher**
* `pipx`
* `conda` (for development)
* `ollama` (a non-thinking ollama model is advised)

## Installation

### Normal (User) Installation

Use this if you just want to install and run the package:

```bash
pipx install .
```

This installs the package in an isolated environment and makes the CLI (if any) available globally.

### Development Installation

Use this if you plan to work on the codebase:

```bash
pipx install --editable .
```

This installs the project in editable mode so changes to the source code take effect immediately.

## Development Setup (Conda)

### 1. Create the Conda Environment

Create the development environment from the provided `env.yml` file:

```bash
conda env create -f env.yml
```

### 2. Activate the Environment

Activate the environment:

```bash
conda activate rubbersoul
```

### 3. Update the Environment

If dependencies change, update the environment and remove unused packages:

```bash
conda env update -f env.yml --prune
```

## How to use

Start by defining the model with:

```sh
rubbersoul -m [model_name]
```

Them run the program (can take a while, not much...) and it will return the commit message.
Them grep it, pip it, use xclip on it or do whatever the f you want with it.
