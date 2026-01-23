
# Recommendations for local Development on Windows and WSL2

### Using Docker on WSL2/22.04

Ubuntu 22.04 LTS uses `iptables-nft` by default.
Switch to `iptables-legacy` so that Docker will work:
https://crapts.org/2022/05/15/install-docker-in-wsl2-with-ubuntu-22-04-lts/

### Copy selection on selecting test (without need for Ctrl-C)

On traditional X11 and KDE Plasma, selected text is automatically copied
to the X selection/clipboard for pasting it. To use this engrained behavior
on Windows as well, it seems the only reliable way to have it for all apps
is a `AutoHotKey` script:

- https://www.ilovefreesoftware.com/30/tutorial/auto-copy-selected-text-clipboard-windows-10.html

While individual extensions for VS Code, Firefox, chrome do work partially,
they either don't cover the Firefox URL bar, the VS Code terminal and so on:

- https://addons.mozilla.org/en-GB/firefox/addon/copy-on-select
- https://marketplace.visualstudio.com/items?itemName=dinhani.copy-on-select (VS Code)
- https://www.jackofalladmins.com/knowledge%20bombs/dev%20dungeon/windows-terminal-copy-selection/
