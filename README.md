# Tech Trand

A Python project using [uv](https://github.com/astral-sh/uv) for dependency management and running commands.

## Setup

1. Install uv:
   ```sh
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```
2. Install dependencies:
   ```sh
   uv pip install -r requirements.txt
   ```
3. Run your project:
   ```sh
   uv pip run python src/main.py
   ```

## Project Structure
- `src/` - Source code
- `tests/` - Test code
- `README.md` - Project documentation
- `pyproject.toml` - Project metadata and dependencies
- `.gitignore` - Files to ignore in git
