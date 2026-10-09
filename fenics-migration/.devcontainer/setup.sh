#!/usr/bin/env bash
set -e # Exit immediately if a command exits with a non-zero status

chsh -s $(which zsh) root || true
if ! command -v starship &> /dev/null; then
  echo "Installing Starship prompt..."
  curl -sS https://starship.rs/install.sh | sh -s -- -y
fi
# Make `legacy <command>` available for running code in the legacy FEniCS container
ln -sf /home/shared/.devcontainer/legacy /usr/local/bin/legacy
echo "Container setup complete!"
