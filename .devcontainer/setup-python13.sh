#!/usr/bin/env bash
set -e

echo "=== Installing pyenv ==="
if [ ! -d "$HOME/.pyenv" ]; then
  curl https://pyenv.run | bash
fi

# Add pyenv to PATH and init
if ! grep -q 'pyenv init' ~/.bashrc; then
  echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
  echo 'eval "$(pyenv init -)"' >> ~/.bashrc
  echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
fi

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

echo "=== Installing build dependencies ==="
sudo apt-get update
sudo apt-get install -y \
  build-essential zlib1g-dev libssl-dev libbz2-dev libreadline-dev \
  libsqlite3-dev libffi-dev liblzma-dev tk-dev wget curl

echo "=== Installing Python 3.13 with pyenv ==="
if ! pyenv versions | grep -q "3.13.1"; then
  pyenv install 3.13.1
fi

echo "=== Setting Python 3.13 as global ==="
pyenv global 3.13.1

echo "=== Done. Python version: $(python --version) ==="
