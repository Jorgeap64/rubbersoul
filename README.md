# rubbersoul
f commits

---

## Requirements

* Python **3.11 or higher**
* `pipx`
* `conda` (for development)

---

## Installation

### Normal (User) Installation

Use this if you just want to install and run the package:

```bash
pipx install .
```

This installs the package in an isolated environment and makes the CLI (if any) available globally.

---

### Development Installation

Use this if you plan to work on the codebase:

```bash
pipx install --editable .
```

This installs the project in editable mode so changes to the source code take effect immediately.

---

## Development Setup (Conda)

### 1. Create the Conda Environment

Create the development environment from the provided `env.yml` file:

```bash
conda env create -f env.yml
```

---

### 2. Activate the Environment

Activate the environment:

```bash
conda activate rubbersoul
```

---

### 3. Update the Environment

If dependencies change, update the environment and remove unused packages:

```bash
conda env update -f env.yml --prune
```

