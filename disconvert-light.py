import os
import subprocess
import shutil
import hashlib
import time
import math
import re

def init():
    set_global_variables_from_file()
    
def set_global_variables_from_file():
    global current_directory
    global discord_folder
    
    with open('paths.txt', 'r') as file:
        lines = file.readlines()
        
        # Disregard the first line (comment)
        if len(lines) > 1:
            current_directory = lines[1].strip()
        if len(lines) > 2:
            discord_folder = lines[2].strip()
    print("User-defined Directory:\n", current_directory)
    print("Directory for shrunk videos:\n", discord_folder)

def generate_file_hash(file_path):
    """Generates a unique hash for a file based on its contents."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_processed_files():
    """Loads processed files from a tracking file."""
    if os.path.exists("processed_videos.txt"):
        with open("processed_videos.txt", "r") as f:
            return {line.strip() for line in f}
    return set()

def save_processed_file(file_hash):
    """Saves a processed file hash to the tracking file."""
    with open("processed_videos.txt", "a") as f:
        f.write(file_hash + "\n")

def get_video_codec(file_path):
    """Returns the codec of a video file using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

def get_video_info(file_path):
    """Gets video information using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()

def parse_fps(info):
    """Parses the FPS from ffprobe output."""
    if '/' in info:
        num, den = info.split('/')
        try:
            return float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            return 30.0  # Default FPS if parsing fails
    return 30.0  # Default FPS if format is unexpected

def compress_video(input_file, output_file, max_size_mb=10):
    """Compresses video until it's under the specified size."""
    crf = 28  # Start with moderate compression
    min_crf = 18  # Minimum CRF (higher quality)
    max_crf = 51  # Maximum CRF (lower quality)
    
    while crf <= max_crf:
        cmd = [
            "ffmpeg", "-i", input_file,
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", str(crf),
            "-c:a", "aac",
            "-b:a", "128k",
            output_file
        ]
        
        # Run ffmpeg command
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check if output file exists and its size
        if os.path.exists(output_file):
            file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            
            if file_size_mb <= max_size_mb:
                return True  # Success
            else:
                # Increase compression if file is still too large
                crf += 2
                os.remove(output_file)  # Remove the too-large file
        else:
            print("Error: Output file not created")
            return False
    
    return False  # Failed to compress under max size

def reencode_video(file_path, reencoded_files, processed_files):
    """Re-encodes a video to H.264 without losing quality."""
    file_hash = generate_file_hash(file_path)
    if file_hash in processed_files:
        return
    
    original_codec = get_video_codec(file_path)
    print(f"Found video {os.path.basename(file_path)} with codec: {original_codec}\n")
    
    if original_codec == "h264":
        save_processed_file(file_hash)
        print(f"File: {os.path.basename(file_path)} doesn't have a saved md5 hash fingerprint in processed_videos.txt...\n\nGenerating hash:\nFilename: {os.path.basename(file_path)}\nSize: {os.path.getsize(file_path)} bytes\nHash: {file_hash}")
        print("Skipping re-encode... \n")
        return
    
    temp_file = f"{file_path}.temp.mp4"
    
    print(f"Re-encoding {os.path.basename(file_path)} / {original_codec} to H.264\n")
    
    cmd = [
        "ffmpeg", "-i", file_path, "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "128k", temp_file
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(temp_file):
        os.replace(temp_file, file_path)
        reencoded_files.append(os.path.basename(file_path))
        save_processed_file(file_hash)
    
    # Check if file is over 10MB and create a Discord-approved version
    if os.path.getsize(file_path) > 10 * 1024 * 1024:
        os.makedirs(discord_folder, exist_ok=True)
        discord_file = os.path.join(discord_folder, "shrunk_video_" + os.path.basename(file_path))
        print(f"Found large video:\nName: {os.path.basename(file_path)}\nSize: {os.path.getsize(file_path)} bytes\nCodec: {original_codec}\n")
        print("Trying to create a Discord-approved version (<10MB)...\n")
        
        # Use the new compress_video function with retry logic
        if compress_video(file_path, discord_file, max_size_mb=10):
            print(f"Successfully created compressed version: {os.path.basename(discord_file)}")
            print(f"Final size: {os.path.getsize(discord_file) / (1024 * 1024):.2f} MB\n")
        else:
            print(f"Failed to compress video under 10MB: {os.path.basename(file_path)}\n")

def main():
    """Main function to process all video files in the current directory."""
    print("Initializing...")
    init()
    video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv")
    reencoded_files = []
    processed_files = load_processed_files()
    vids = 0
    files = 0
    print(f"Video extensions: {video_extensions}")
    print("Initializing complete!\n")
    print(f"Checking all files within: {current_directory}\n")
    for filename in os.listdir(current_directory):
        files = files + 1
        if filename.lower().endswith(video_extensions):
            file_path = os.path.join(current_directory, filename)
            reencode_video(file_path, reencoded_files, processed_files)
            vids = vids + 1
    print(f"Found total of: {files} files of which {vids} are video files\n")
    print(f"All {vids} video files checked!\n")
    time.sleep(5)
    
    if reencoded_files:
        print("Re-encoded files:")
        for file in reencoded_files:
            print(file)
        input("\nPress ENTER to continue...")

if __name__ == "__main__":
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is not installed. Please install it first.")
    else:
        main()