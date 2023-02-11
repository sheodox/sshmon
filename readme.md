# SSH Monitor

A simple GTK+ GUI for opening SSH sessions to your remotes. Run using `python3 sshmon.py`.

![screenshot](https://raw.githubusercontent.com/sheodox/sshmon/master/images/screenshot.png)

There is also a CLI which lets you open an SSH session from the terminal, though you will need to use the GUI for managing remotes. The CLI uses the same config file as the GUI program, but just prints the list of remotes and prompts for a number matching the remote you want to connect to.

## CLI Setup

1. [Install Go](https://go.dev/)
1. Run `go build` to build the CLI
1. Run `./sshmon` to start
