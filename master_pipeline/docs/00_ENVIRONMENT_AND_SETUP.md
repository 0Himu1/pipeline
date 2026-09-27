# Environment Setup, Dependencies & Prerequisites Guide

This document is a complete, self-contained technical guide for any AI agent or human developer to set up the execution environment, runtime dependencies, system tools, and MCP server integrations required to run the Story Video Production Pipeline.

*(Note: CapCut Desktop and Antigravity IDE installations are excluded from this guide as they are assumed to be pre-installed.)*

---

## 1. System Requirements

- **Operating System**: Windows 10 / Windows 11 (64-bit)
- **Shell**: PowerShell 7 (`pwsh`) or Windows PowerShell 5.1 (`powershell`)
  - Execution policy must allow script execution:
    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    ```

---

## 2. Runtime Dependencies

### A. Python 3.10+ (Recommended: Python 3.12)
Python powers the DSP audio trimming, speech pause detection, and image matching engines.

1. **Installation** (if not already present):
   ```powershell
   winget install Python.Python.3.12
   ```
2. **Verify Python & Pip in PATH**:
   ```powershell
   python --version
   pip --version
   ```
3. **Required Python Packages**:
   Install `pydub`, `edge-tts`, and `requests`:
   ```powershell
   pip install pydub edge-tts requests
   ```

---

### B. Node.js (v18+ or v20+ LTS)
Node.js executes the fast JSON stream builder that generates the CapCut draft timeline, keyframes, and layout configurations.

1. **Installation** (if not already present):
   ```powershell
   winget install OpenJS.NodeJS.LTS
   ```
2. **Verify Node & NPM in PATH**:
   ```powershell
   node -v
   npm -v
   ```

---

### C. FFmpeg & FFprobe (Critical for Audio Processing)
`pydub` strictly requires `ffmpeg` and `ffprobe` binaries in the system `PATH` to decode MP3 files, read audio metadata, and export 320kbps MP3 / 16-bit WAV files.

1. **Installation via Winget**:
   ```powershell
   winget install Gyan.FFmpeg
   ```
   *(Or download the release build from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) and place `bin/` in your Windows Environment `PATH`.)*

2. **Verification**:
   ```powershell
   ffmpeg -version
   ffprobe -version
   ```
   > [!IMPORTANT]
   > If `ffmpeg` is not in `PATH`, `pydub` will fail silently or throw `FileNotFoundError` when exporting MP3 audio.

---

## 3. CapCut MCP Server Integration (Optional / Native Mode)

The pipeline can run either **Directly via Scripts** (fastest, no daemon needed) or via **CapCut MCP Tools** (`capcut-mcp-server`).

### A. Clone & Build `capcut-mcp-server`
```powershell
# Clone repository
git clone https://github.com/0xHimu/capcut-mcp-server.git "D:\Himu\capcut-mcp-server"

# Install and build TypeScript distribution
cd "D:\Himu\capcut-mcp-server"
npm install
npm run build
```
*(Produces `D:\Himu\capcut-mcp-server\dist\index.js`)*

### B. Configure Antigravity MCP Server Registry
Add the server entry to the global Antigravity MCP configuration file:
📍 **`C:\Users\<YOUR_USER>\.gemini\config\mcp_config.json`**

```json
{
  "mcpServers": {
    "capcut": {
      "command": "node",
      "args": [
        "D:/Himu/capcut-mcp-server/dist/index.js"
      ]
    }
  }
}
```

### C. Available MCP Tools Reference
Once configured, the following tools become available to the agent:
- `capcut_create_draft`: Initializes a blank project.
- `capcut_add_video`: Appends video/image segments to track 0.
- `capcut_add_audio`: Appends audio segments to track 1.
- `capcut_add_text`: Injects titles and subtitles.
- `capcut_add_keyframe`: Injects scale/position keyframes.
- `capcut_add_effect`: Attaches visual effects.
- `capcut_save_draft`: Flushes draft JSON to disk.

---

## 4. CapCut Drafts Directory Configuration

CapCut Desktop stores all local user projects at:
```
%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\
```
*(Typically: `C:\Users\<YOUR_USERNAME>\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\`)*

### Directory Invariants:
- The agent must verify write permissions to this folder.
- `root_meta_info.json` exists in this folder and tracks all active projects.
- CapCut Desktop should be closed when modifying drafts to avoid file locking collisions.

---

## 5. Antigravity Agent Configuration & Permissions

When delegating this task to an Antigravity agent or subagent, ensure the following permissions are granted:
1. **Run Command Tool (`run_command`)**: Needed to execute Python trimming, Node building, and FFmpeg transcoding.
2. **File Tools (`view_file`, `write_to_file`, `replace_file_content`)**: Needed to write scripts, manifests, and inspect drafts.
3. **Workspace Path**: `d:\Himu\Luna` (or your active project repository).
4. **App Data Access**: Read/write access to `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\`.

---

## 6. Pre-Flight Diagnostic Check (Doctor Script)

Run this one-liner in PowerShell to verify that the entire environment is 100% operational:

```powershell
& python -c "
import sys, shutil
print('Python: ' + sys.version.split()[0] + ' [OK]')
try:
    import pydub
    print('Pydub: installed [OK]')
except ImportError:
    print('Pydub: MISSING (run: pip install pydub) [FAIL]')
try:
    import edge_tts
    print('edge-tts: installed [OK]')
except ImportError:
    print('edge-tts: MISSING (run: pip install edge-tts) [FAIL]')
print('Node.js: ' + ('found [OK]' if shutil.which('node') else 'MISSING [FAIL]'))
print('FFmpeg: ' + ('found [OK]' if shutil.which('ffmpeg') else 'MISSING [FAIL]'))
print('FFprobe: ' + ('found [OK]' if shutil.which('ffprobe') else 'MISSING [FAIL]'))
import os
capcut_dir = os.path.expandvars(r'%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft')
print('CapCut Drafts Dir: ' + ('found [OK]' if os.path.exists(capcut_dir) else 'NOT FOUND [WARN]'))
"
```

If all checks report `[OK]`, the environment is completely ready to produce story videos!
