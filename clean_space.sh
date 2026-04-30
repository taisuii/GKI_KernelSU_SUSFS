#!/bin/bash
# clean_space.sh - Aggressive disk cleanup for CI runners or local use
# Usage: bash clean_space.sh

set -e

# Remove Android SDKs and packages
echo "Removing Android SDKs and packages..."
sudo rm -rf /usr/local/lib/android /opt/android /usr/local/android-sdk /home/runner/Android || true
ANDROID_PKGS=$(dpkg -l | grep -E "^ii.*(android|adb)" | awk '{print $2}' | tr '\n' ' ')
if [ -n "$ANDROID_PKGS" ]; then
  sudo apt-get remove -y $ANDROID_PKGS || true
  sudo apt-get autoremove -y || true
  sudo apt-get clean || true
fi

# Remove .NET SDKs and packages
echo "Removing .NET SDKs and packages..."
sudo rm -rf /usr/share/dotnet /usr/share/doc/dotnet-* || true
DOTNET_PKGS=$(dpkg -l | grep -E "^ii.*dotnet" | awk '{print $2}' | tr '\n' ' ')
if [ -n "$DOTNET_PKGS" ]; then
  sudo apt-get remove -y $DOTNET_PKGS || true
  sudo apt-get autoremove -y || true
  sudo apt-get clean || true
fi

# Remove Haskell SDKs and packages
echo "Removing Haskell SDKs and packages..."
sudo rm -rf /opt/ghc /usr/local/.ghcup /opt/cabal /home/runner/.ghcup /home/runner/.cabal || true
HASKELL_PKGS=$(dpkg -l | grep -E "^ii.*(ghc|haskell|cabal)" | awk '{print $2}' | tr '\n' ' ')
if [ -n "$HASKELL_PKGS" ]; then
  sudo apt-get remove -y $HASKELL_PKGS || true
  sudo apt-get autoremove -y || true
  sudo apt-get clean || true
fi

# Remove tool cache (set AGENT_TOOLSDIRECTORY if needed)
if [ -n "$AGENT_TOOLSDIRECTORY" ]; then
  echo "Removing tool cache at $AGENT_TOOLSDIRECTORY..."
  sudo rm -rf "$AGENT_TOOLSDIRECTORY" || true
fi

# Remove swap storage
echo "Removing swap storage..."
sudo swapoff -a || true
sudo rm -f /mnt/swapfile || true

# Remove extra large folders (add your own as needed)
# Example: sudo rm -rf /path/to/large/folder

# Done
echo "Disk cleanup complete."
