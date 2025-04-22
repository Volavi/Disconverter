# 🎥 Video Processor for Discord

A simple script that converts videos to Discord-friendly formats and compresses them under 10MB.

## Why I Made This

- Ylilauta.org videos wouldn't play in Discord
- Wanted to share videos without Nitro subscription (10MB limit)
- Got tired of manually converting files and using websites such as 8mbvideo

## What It Does

1. Goes through all files within a folder
2. Converts all videos to H.264 (plays everywhere)
3. Makes compressed copies under 10MB for Discord
4. Remembers which files it's already processed with hashing

## 🔧 How To Use

1. Clone this [repository](https://github.com/Volavi/Disconverter/archive/refs/heads/main.zip)
2. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`
<details>
<summary>📥 FFmpeg Install to PATH (via Chocolatey)</summary>

### Command Prompt (Admin):
```cmd
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin" && choco install ffmpeg -y
```

### PowerShell (Admin):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')); choco install ffmpeg -y
```

> **Note**  
> - Run as Administrator  
> - The `-y` flag auto-confirms installations  
> - Adds FFmpeg to PATH automatically
</details>

2. Make sure that `paths.txt` is in the same folder with the script.
3. Type your media paths in the `paths.txt` on marked rows (don't include the "{}" -chars)
4. Run the script
5. Post memes


## ⚙️ Requirements

- Python 3+
- FFmpeg installed and in PATH (google how to install for your OS and how to set in PATH)

## 💀 Disclaimer

Use at your own risk. I'm not responsible if:
- Your videos get messed up
- Discord still won't accept them
- Your computer explodes

(Make backups first)
