# rubbersoul

I don't like to write them, you don't like to write them, so f it let the llm do it.

## Requirements

* Python **3.14 or higher**
* `uv` (for development)
* `ollama` (a non-thinking ollama model is advised)

## Installation

### Normal (User) Installation

Use this if you just want to install and run the package:

```bash
uv tool install .
```

To update it:
```sh
uv tool upgrade rubbersoul
```

If is annoying:
```sh
uv tool install . --uninstall
```

This installs the package in an isolated environment and makes the CLI (if any) available globally.

### Dev Mode
Set up `.env` (see `.env.example`), then run:
```bash
uv run rubbersoul
```

This installs the project in editable mode so changes to the source code take effect immediately.

## Development Setup (uv)

### Create the uv Environment

```bash
uv sync
```

## How to use

Start by defining the model with (it saves the model for later usage):

```sh
uv run rubbersoul -m [model_name]
```

Them run the program (can take a while, not much...) and it will return the commit message.
Them grep it, pip it, use xclip on it or do whatever the f you want with it.

---

![](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwallpapers.com%2Fimages%2Fhd%2Fnicolas-cage-meme-galaxy-cupcake-bp25b4d3byu6a79o.jpg&f=1&nofb=1&ipt=5c358dd877e8dc26ce8e7a2200de6509f699b8ebd1a9f8e183a705b82426602c)
