@echo off
title ComfyUI Tunnel (Git Bash ssh) - keep this window open
echo ============================================
echo  ComfyUI tunnel - uses Git Bash OpenSSH 10.3
echo  (Windows built-in ssh is incompatible with
echo   the VS Code forward bridge - MAC errors)
echo  Browser: http://127.0.0.1:8188
echo  Keep this window open. Ctrl+C to stop.
echo ============================================
start "" http://127.0.0.1:8188

set SSH_EXE=<你的ssh.exe路径，推荐Git Bash自带的OpenSSH>

:loop
echo [%time%] connecting...
"%SSH_EXE%" -N -L 8188:127.0.0.1:8188 -p <你的SSH端口> developer@127.0.0.1 -i <你的KEY路径> -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o TCPKeepAlive=yes -o ExitOnForwardFailure=yes -o ConnectTimeout=20
echo [%time%] tunnel dropped, waiting 15 seconds before reconnect...
ping -n 16 127.0.0.1 >nul
goto loop
