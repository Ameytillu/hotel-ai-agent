@echo off
REM ngrok_setup.bat
REM ---------------
REM This script launches ngrok to expose your local Flask/FastAPI server
REM running on port 8000 to the internet.  Once ngrok starts, it
REM prints a public HTTPS URL.  You will copy that URL into the
REM Twilio console (Voice settings) so that Twilio can reach your
REM server for inbound calls.

REM Ensure ngrok is installed and on your PATH.  Download from:
REM https://ngrok.com/download

REM Change the port number below if your voice server runs on a
REM different port.
set PORT=8000
echo Starting ngrok tunnel on port %PORT%...
ngrok http %PORT%
pause