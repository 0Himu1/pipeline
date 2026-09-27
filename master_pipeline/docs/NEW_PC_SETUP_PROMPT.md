# 1-Click Agent Setup Prompt for Brand New PC

Copy and paste the exact prompt below into your Antigravity (or AI coding agent) chat on the new PC immediately after extracting `Luna_Project_Master.zip`.

---

```text
You are Antigravity, the AI pair programmer on this new PC.
This machine is completely fresh and does NOT have the required tools, runtime dependencies, or servers installed yet.

Your objective is to inspect this workspace, read the setup guides, install all necessary system tools and packages, configure the CapCut MCP server, and run the diagnostic check so the workstation is 100% aligned and ready to produce story videos.

Please execute the following steps in sequence:

1. READ THE SPECIFICATION:
   - Read "master_pipeline/docs/00_ENVIRONMENT_AND_SETUP.md" and "master_pipeline/README.md".

2. INSTALL RUNTIME DEPENDENCIES (via Windows winget / PowerShell):
   - Check if Python is installed; if not, install Python 3.12:
     winget install Python.Python.3.12 --silent
   - Check if Node.js is installed; if not, install Node.js LTS:
     winget install OpenJS.NodeJS.LTS --silent
   - Check if FFmpeg / FFprobe is in PATH; if not, install Gyan FFmpeg:
     winget install Gyan.FFmpeg --silent
   - Ensure PowerShell script execution policy is enabled:
     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

3. INSTALL PYTHON AUDIO, SYNTHESIS & GRAPHICS PACKAGES:
   - Run: pip install pydub edge-tts pillow requests

4. CONFIGURE CAPCUT MCP SERVER:
   - Locate the "capcut-mcp-server" folder in this workspace.
   - Run "npm install" inside "capcut-mcp-server" to ensure dependencies are resolved.
   - Register the CapCut MCP server in the Antigravity MCP configuration file at:
     "%USERPROFILE%\.gemini\antigravity\mcp_config.json" (or "%USERPROFILE%\.gemini\config\mcp_config.json"):
     {
       "mcpServers": {
         "capcut": {
           "command": "node",
           "args": [
             "<ABSOLUTE_PATH_TO_WORKSPACE>/capcut-mcp-server/dist/index.js"
           ]
         }
       }
     }

5. VERIFY CAPCUT DESKTOP INTEGRATION:
   - Verify that the local CapCut draft directory exists:
     "%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\"
   - If CapCut has never been opened on this PC, create this directory or prompt me to launch CapCut Desktop once.

6. RUN PRE-FLIGHT DIAGNOSTIC DOCTOR CHECK:
   - Execute the diagnostic command:
     python -c "import sys, shutil, os, pydub, edge_tts, PIL; print('Python: ' + sys.version.split()[0] + ' [OK]'); print('Pydub: [OK]'); print('edge-tts: [OK]'); print('Pillow: [OK]'); print('Node.js: ' + ('[OK]' if shutil.which('node') else '[FAIL]')); print('FFmpeg: ' + ('[OK]' if shutil.which('ffmpeg') else '[FAIL]')); print('FFprobe: ' + ('[OK]' if shutil.which('ffprobe') else '[FAIL]')); capcut_dir = os.path.expandvars(r'%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft'); print('CapCut Drafts Dir: ' + ('[OK]' if os.path.exists(capcut_dir) else '[WARN: CapCut not run once]'))"
   - Test CLI availability: python master_pipeline/scripts/run_pipeline.py --help

7. CONFIRMATION:
   - Report back with a clear status checklist confirming that Python, FFmpeg, edge-tts, pydub, Node.js, and CapCut MCP are verified and aligned.
   - Let me know when you are ready for me to place my first "Script.txt" in "projects/<New Story Name>".
```
