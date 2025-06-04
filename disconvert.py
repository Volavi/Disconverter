import os
import subprocess
import shutil
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

class VideoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disconvert")
        self.root.geometry("700x500")
        
        # Variables
        self.current_directory = ""
        self.discord_folder = ""
        self.is_running = False
        self.processed_files = set()
        self.reencoded_files = []
        self.video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv")
        self.total_files = 0
        self.video_files = 0
        self.processed_count = 0
        self.current_file = ""
        self.show_debug = False
        
        # Try to read paths from file first
        self.read_paths_from_file()
        
        # UI Elements
        self.create_widgets()
        
        # Check ffmpeg
        if shutil.which("ffmpeg") is None:
            messagebox.showerror("Error", "ffmpeg is not installed. Please install it first.")
            self.root.destroy()
    
    def read_paths_from_file(self):
        """Read input and output directories from paths.txt if it exists"""
        try:
            if os.path.exists('paths.txt'):
                with open('paths.txt', 'r') as file:
                    lines = file.readlines()
                    if len(lines) > 1:
                        self.current_directory = lines[1].strip()
                    if len(lines) > 2:
                        self.discord_folder = lines[2].strip()
        except Exception as e:
            print(f"Error reading paths.txt: {e}")
    
    def save_paths_to_file(self):
        """Save current directories to paths.txt"""
        try:
            with open('paths.txt', 'w') as file:
                file.write("# Paths configuration\n")
                file.write(f"{self.current_directory}\n")
                file.write(f"{self.discord_folder}\n")
        except Exception as e:
            print(f"Error saving paths.txt: {e}")
    
    def create_widgets(self):
        # Configure styles
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TFrame', padding=10)
        style.configure('TLabelframe', padding=10)
        style.configure('TLabelframe.Label', padding=5)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directories", padding="5")
        dir_frame.pack(fill=tk.X, pady=10)
        
        # Directory labels
        label_frame = ttk.Frame(dir_frame, padding="1")
        label_frame.pack(fill=tk.X, pady=1)
        
        self.source_dir_label = ttk.Label(label_frame, text=f"Source of memes: {self.current_directory or 'Not set'}")
        self.source_dir_label.pack(fill=tk.X, padx=5, pady=5)
        
        self.output_dir_label = ttk.Label(label_frame, text=f"Output for compressed videos: {self.discord_folder or 'Not set'}")
        self.output_dir_label.pack(fill=tk.X, padx=5, pady=5)

        # Button frame
        button_frame = ttk.Frame(dir_frame, padding="5")
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Set Source Directory", command=self.set_source_dir).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(button_frame, text="Set Output Directory", command=self.set_output_dir).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Progress area
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Status: Ready", font=('Helvetica', 10, 'bold'))
        self.status_label.pack(fill=tk.X, pady=5)
        
        # Progress counter
        self.counter_label = ttk.Label(progress_frame, 
                                     text="0/0 files processed (0 videos found)")
        self.counter_label.pack(fill=tk.X, pady=5)
        
        # Current file label
        self.current_file_label = ttk.Label(progress_frame, text="Current file: None", 
                                          wraplength=650, anchor=tk.W)
        self.current_file_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Debug console toggle
        self.debug_toggle = ttk.Button(progress_frame, text="▼ Show Debug Console",
                                     command=self.toggle_debug)
        self.debug_toggle.pack(fill=tk.X, pady=5)
        
        # Debug console (initially hidden)
        self.debug_frame = ttk.Frame(progress_frame)
        self.log_text = tk.Text(self.debug_frame, height=7, state=tk.DISABLED, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.debug_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Processing", 
                                     command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.redo_button = ttk.Button(control_frame, text="Redo", 
                                    command=self.redo_processing, state=tk.DISABLED)
        self.redo_button.pack(side=tk.LEFT, padx=15, pady=5)
        
        ttk.Button(control_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=15, pady=5)
    
    def toggle_debug(self):
        """Toggle debug console visibility"""
        self.show_debug = not self.show_debug
        if self.show_debug:
            self.debug_frame.pack(fill=tk.BOTH, expand=True)
            self.debug_toggle.config(text="▲ Hide Debug Console")
            self.root.geometry("700x700")
        else:
            self.debug_frame.pack_forget()
            self.debug_toggle.config(text="▼ Show Debug Console")
            self.root.geometry("700x500")
    
    def update_status(self, message):
        """Update the main status label"""
        self.status_label.config(text=f"Status: {message}")
        self.root.update()
    
    def set_source_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.current_directory = directory
            self.source_dir_label.config(text=f"Source: {directory}")
            self.save_paths_to_file()
    
    def set_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.discord_folder = directory
            self.output_dir_label.config(text=f"Output: {directory}")
            self.save_paths_to_file()
    
    def start_processing(self):
        if not self.current_directory or not self.discord_folder:
            messagebox.showwarning("Warning", "Please set both source and output directories")
            return
            
        if self.is_running:
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.redo_button.config(state=tk.DISABLED)
        self.processed_count = 0
        self.reencoded_files = []
        
        # Clear log and reset UI
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        self.current_file_label.config(text="Current file: None")
        
        # Start processing
        threading.Thread(target=self.process_videos, daemon=True).start()
    
    def redo_processing(self):
        """Simply restart the processing without clearing anything"""
        self.start_processing()
    
    def update_counter(self):
        """Update the counter label with current progress"""
        self.counter_label.config(
            text=f"{self.processed_count}/{self.video_files} files processed ({self.video_files} videos found)"
        )
        self.root.update()
    
    def process_videos(self):
        self.update_status("Initializing")
        self.debug_message("Initializing...")
        self.processed_files = self.load_processed_files()
        
        self.update_status("Checking files")
        self.debug_message(f"Video extensions: {self.video_extensions}")
        self.debug_message(f"Checking all files within: {self.current_directory}")
        
        # Count files first for progress
        file_list = os.listdir(self.current_directory)
        self.total_files = len(file_list)
        self.video_files = sum(1 for f in file_list if f.lower().endswith(self.video_extensions))
        self.update_counter()
        
        if self.video_files == 0:
            self.update_status("Ready (no videos found)")
            self.debug_message("No video files found!")
            self.processing_complete()
            return
            
        self.progress_bar["maximum"] = self.video_files
        
        # Process files
        for filename in os.listdir(self.current_directory):
            if not self.is_running:  # Allow stopping if needed
                break
                
            if filename.lower().endswith(self.video_extensions):
                self.current_file = filename
                self.current_file_label.config(text=f"Current file: {filename}")
                file_path = os.path.join(self.current_directory, filename)
                
                self.reencode_video(file_path)
                self.processed_count += 1
                self.progress_bar["value"] = self.processed_count
                self.update_counter()
                self.root.update()
        
        self.update_status("Complete")
        self.debug_message(f"\nProcessing complete: {self.video_files} video files processed")
        
        if self.reencoded_files:
            self.debug_message("\nRe-encoded files:")
            for file in self.reencoded_files:
                self.debug_message(file)
        
        self.processing_complete()
    
    def processing_complete(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.redo_button.config(state=tk.NORMAL)
        self.current_file_label.config(text="Current file: None")
    
    def debug_message(self, message):
        """Add message to debug console only"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def load_processed_files(self):
        if os.path.exists("processed_videos.txt"):
            with open("processed_videos.txt", "r") as f:
                return {line.strip() for line in f}
        return set()
    
    def generate_file_hash(self, file_path):
        self.update_status("Checking file/hash...")
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def save_processed_file(self, file_hash):
        self.update_status("Writing hash")
        with open("processed_videos.txt", "a") as f:
            f.write(file_hash + "\n")
    
    def get_video_codec(self, file_path):
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", 
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    
    def compress_video(self, input_file, output_file, max_size_mb=10):
        crf = 28
        min_crf = 18
        max_crf = 51
        
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
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(output_file):
                file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
                
                if file_size_mb <= max_size_mb:
                    return True
                else:
                    crf += 2
                    os.remove(output_file)
            else:
                self.debug_message("Error: Output file not created")
                return False
        
        return False
    
    def reencode_video(self, file_path):
        file_hash = self.generate_file_hash(file_path)
        if file_hash in self.processed_files:
            return
        
        original_codec = self.get_video_codec(file_path)
        self.update_status(f"Checking: {os.path.basename(file_path)}")
        self.debug_message(f"Processing: {os.path.basename(file_path)} (Codec: {original_codec})")
        
        if original_codec == "h264":
            self.save_processed_file(file_hash)
            self.debug_message(f"Skipping (already H.264): {os.path.basename(file_path)}\n")
            return
        
        temp_file = f"{file_path}.temp.mp4"
        self.update_status(f"Converting: {os.path.basename(file_path)}")
        self.debug_message(f"Re-encoding to H.264: {os.path.basename(file_path)}")
        
        cmd = [
            "ffmpeg", "-i", file_path, "-c:v", "libx264", "-preset", "slow", 
            "-crf", "18", "-c:a", "aac", "-b:a", "128k", temp_file
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(temp_file):
            os.replace(temp_file, file_path)
            self.reencoded_files.append(os.path.basename(file_path))
            self.save_processed_file(file_hash)
        
        # Create Discord version if needed
        if os.path.getsize(file_path) > 10 * 1024 * 1024:
            os.makedirs(self.discord_folder, exist_ok=True)
            discord_file = os.path.join(self.discord_folder, "shrunk_" + os.path.basename(file_path))
            self.update_status(f"Compressing: {os.path.basename(file_path)}")
            self.debug_message(f"Compressing for Discord: {os.path.basename(file_path)}")
            
            if self.compress_video(file_path, discord_file, max_size_mb=10):
                self.debug_message(f"Created: {os.path.basename(discord_file)} ({os.path.getsize(discord_file) / (1024 * 1024):.2f} MB)\n")
            else:
                self.debug_message(f"Failed to compress: {os.path.basename(file_path)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCompressorApp(root)
    root.mainloop()