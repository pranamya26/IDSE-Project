# LAN Whiteboard
Requires Python 3.9+ (tkinter included). No third-party packages.

## Run
Server (one machine):  python server.py [port]   (default 5050; prints its LAN IP)
Client (each user):    python client.py
- Host: enter server IP, username, a room code, optional password -> "Create session"
- Others: same IP and room code (+ password) -> "Join session"
- Open TCP port 5050 in the server's firewall.

## Build executables (build on the OS you will demo on)
pip install pyinstaller
pyinstaller --onefile server.py
pyinstaller --onefile --windowed client.py
