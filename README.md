# LXQT-Linux-VM

Run the full LXQt desktop, including the Fancy Menu, in GitHub Codespaces and
access it from a browser using noVNC.

## Automatic desktop startup

The desktop starts automatically every time the Codespace container starts.
After adding or changing the dev container configuration, run
**Codespaces: Rebuild Container** once from the VS Code Command Palette.
Codespaces then forwards port `6080` and opens the browser-based desktop. If it
does not open automatically, select port `6080` in the **Ports** tab and open it
in a browser.

Commit and push `.devcontainer/` to enable this configuration for future
Codespaces created from the repository.

The desktop runs in a virtual X display at 1440x900. The VNC server listens only
on the container's localhost; browser access is provided by the forwarded
noVNC port.

At desktop startup, the managed Fancy Menu application list is restored from
the system's categorized application menu, and every active LXQt menu plugin
is pointed to it. Changes to the managed menu are repaired on desktop restart.
