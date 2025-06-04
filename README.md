# 🎥 Disconverter – Video Compressor for Discord-Unfriendly Media

A simple **GUI** and **CLI** tool that converts and compresses videos to be Discord-friendly — **under 10MB** and **universally playable** (H.264).

## ✨ What's New

* **Sleek user interface** with progress bar, file tracking, and debug console
* Remembers processed files with file hashing
* Still includes the **original lightweight script**: `disconvert-light.py`

---

## 🤔 Why I Made This

* Videos from sites like **Ylilauta.org** wouldn’t play in Discord
* Needed to **bypass Discord’s 8MB/10MB upload limit** without Nitro
* Got tired of **manually converting files** or relying on janky websites like 8mb.video

---

## 🚀 What It Does

1. Goes through all files in a chosen folder
2. Converts non-H.264 videos to H.264 (compatible everywhere)
3. Creates compressed versions under 10MB for Discord sharing
4. Skips already-processed files using smart file hashing
5. Provides a **simple interface** for batch processing with optional debug output

---

## 🖥️ How To Use

### 📦 Option 1: GUI Version

1. Clone or download this repo:
   [Download ZIP](https://github.com/Volavi/Disconverter/archive/refs/heads/main.zip)
2. Install FFmpeg:

   * **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) or use Chocolatey (below)
   * **Linux**: `sudo apt install ffmpeg`
   * **macOS**: `brew install ffmpeg`

<details>
<summary>📥 Install FFmpeg with Chocolatey (Windows, Admin)</summary>

#### CMD:

```cmd
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin" && choco install ffmpeg -y
```

#### PowerShell:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')); choco install ffmpeg -y
```

</details>

3. Install tkinter `pip install tkinter`
3. Run `disconvert.py`
4. Use the interface to:

   * Select a source directory
   * Select an output directory (for compressed videos)
   * Press "Start Processing"
5. Enjoy auto-compression and a debug console if needed
6. Press "Redo" to run again without re-selecting paths

### ⚡ Option 2: Script-Only (Light Mode)

Use `disconvert-light.py` for command-line or automation purposes.

* Edit `paths.txt` and provide:

  * Line 2: Source folder
  * Line 3: Output folder
* Run via terminal or script automation:

```bash
python disconvert-light.py
```

---

## 🛠️ Requirements

* Python 3+
* FFmpeg installed and added to PATH
* Tkinter (should come with Python by default)

---

## 🧪 Tested Formats

* `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`

---

## 💀 Disclaimer

Use at your own risk.
I’m not responsible if:

* Your videos are ruined
* Discord still hates your uploads
* Your PC combusts mid-conversion

**Always keep backups.**
