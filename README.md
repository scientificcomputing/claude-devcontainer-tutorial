# Claude Code in dev containers

This repository is a tutorial on running [Claude Code](https://claude.com/claude-code)
inside [dev containers](https://containers.dev). Each folder is a separate example
with its own `.devcontainer/` configuration. A dev container gives Claude a
reproducible environment that is isolated from your machine. It can install packages,
run tests and break things without touching your host system.

## Examples

| Example | What it shows |
| --- | --- |
| [default](default/) | The smallest useful setup: an Ubuntu base image with zsh, Starship and the Claude Code extension. There is no project code. Use it as a template. |
| [fenicsx-setup](fenicsx-setup/) | The main example. A small FEniCSx package (`biodiff`) for reaction–diffusion in biological tissue, built on the official DOLFINx image. It has tests, ruff/mypy pre-commit hooks and a list of prompts for extending it with Claude ([PROMPT.md](fenicsx-setup/PROMPT.md)). |
| [multiple-fenicsx-setup](multiple-fenicsx-setup/) | Several dev container configs for one project (`stable` and `nightly` DOLFINx), so you can check that code works with both versions. Contains only placeholder code. |
| [spack-env](spack-env/) | A container built from a custom `Dockerfile` instead of a prebuilt image. It installs [Spack](https://spack.io) and registers a local package repository, ready for writing Spack packages. |

## Prerequisites

- A container runtime: [Docker Desktop](https://www.docker.com/products/docker-desktop/),
  [OrbStack](https://orbstack.dev), [Colima](https://github.com/abiosoft/colima) or
  [Podman](https://podman.io).
- [VS Code](https://code.visualstudio.com) with the
  [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  extension.
- A Claude account with access to Claude Code.

The containers bind-mount these files from your home directory, so your shell and git
setup work inside the container:

- `~/.zshrc`
- `~/.oh-my-zsh`
- `~/.ssh` (read-only, for pushing to GitHub)

**The container won't start if any of these files are missing on your machine.**
Create them, or delete the matching lines under `"mounts"` in `devcontainer.json`.

## Opening an example

1. In VS Code, open an **example folder** such as `fenicsx-setup/`, not the repository
   root. VS Code looks for `.devcontainer/` in the folder you open.
2. Run **Dev Containers: Reopen in Container** from the command palette
   (`Cmd/Ctrl+Shift+P`). For `multiple-fenicsx-setup`, VS Code then asks which
   config to use.
3. The first build pulls the image and can take a few minutes.

Without VS Code you can use the [Dev Container CLI](https://github.com/devcontainers/cli):

```bash
npm install -g @devcontainers/cli
devcontainer up --workspace-folder fenicsx-setup
devcontainer exec --workspace-folder fenicsx-setup zsh
```

### What happens when the container starts

Each `devcontainer.json` defines two hooks:

- **`postCreateCommand`** runs [`.devcontainer/setup.sh`](fenicsx-setup/.devcontainer/setup.sh)
  once, when the container is created. It installs the Starship prompt and, where
  there is a Python project, installs it with `pip install -e .[dev]` and sets up
  pre-commit.
- **`postAttachCommand`** runs
  [`.devcontainer/setup-claude-plugins.sh`](fenicsx-setup/.devcontainer/setup-claude-plugins.sh)
  every time VS Code attaches. Claude Code keeps its plugins in `~/.claude`, which
  is lost when the container is rebuilt, so the script reinstalls them (for example
  [superpowers](https://github.com/obra/superpowers)). The script is safe to run
  more than once.

For the same reason you may need to log in to Claude Code again after rebuilding a
container.

## Using Claude Code

Open Claude Code from the Claude icon in the VS Code sidebar, or run `claude` in the
terminal. Some useful commands:

| Command | What it does |
| --- | --- |
| `/init` | Run once in a new project. Claude reads the code and writes a `CLAUDE.md` describing it, which is loaded into every later session. |
| `/clear` | Start a new session with an empty context. |
| `/btw` | Ask a side question without interrupting the current task. |
| `/plugins` | Manage plugins. If a newly installed plugin doesn't show up, run `/reload-plugins`. |
| `/context` | Show how much of the context window is in use. |
| `/compact` | Summarise the conversation so far to free up context while keeping the session going. |
| `Shift+Tab` | Cycle through permission modes, including plan mode, where Claude plans before it edits anything. |

### Tips for writing good prompts

- **Be specific about the problem.** Give the equations, units and boundary
  conditions, or the exact behaviour you want. Don't leave Claude to guess.
- **Say how you'll check the result.** For example: "the total amount must be
  conserved", "the result must converge at second order", or "all tests must pass".
  Claude can then verify its own work.
- **Point to existing code.** For example: "follow the style of `mesh.py`".
- **Ask for a plan first** on larger tasks, or use plan mode.

For a full set of example prompts, see
[fenicsx-setup/PROMPT.md](fenicsx-setup/PROMPT.md).

## License

[MIT](LICENSE)
