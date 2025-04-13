import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess

class VideoInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cutter")
        self.root.geometry("600x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create drag and drop area
        self.drop_area = tk.Label(
            self.main_frame,
            text="Drag and drop video file here",
            relief=tk.RAISED,
            width=50,
            height=10
        )
        self.drop_area.pack(pady=10)
        
        # Create open button
        self.open_button = ttk.Button(
            self.main_frame,
            text="Open Video File",
            command=self.open_file_dialog
        )
        self.open_button.pack(pady=5)
        
        # Create time input frame
        time_frame = ttk.LabelFrame(self.main_frame, text="Cut Time Points", padding="5")
        time_frame.pack(fill=tk.X, pady=5)
        
        # Start time input
        ttk.Label(time_frame, text="Start Time (seconds):").pack(side=tk.LEFT, padx=5)
        self.start_time = ttk.Entry(time_frame, width=10)
        self.start_time.pack(side=tk.LEFT, padx=5)
        
        # End time input
        ttk.Label(time_frame, text="End Time (seconds):").pack(side=tk.LEFT, padx=5)
        self.end_time = ttk.Entry(time_frame, width=10)
        self.end_time.pack(side=tk.LEFT, padx=5)
        
        # Prefix input frame
        prefix_frame = ttk.LabelFrame(self.main_frame, text="Output Prefix", padding="5")
        prefix_frame.pack(fill=tk.X, pady=5)
        
        self.prefix = ttk.Entry(prefix_frame, width=50)
        self.prefix.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Output destination frame
        output_frame = ttk.LabelFrame(self.main_frame, text="Output Destination", padding="5")
        output_frame.pack(fill=tk.X, pady=5)
        
        # Output path entry and browse button
        self.output_path = ttk.Entry(output_frame, width=50)
        self.output_path.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            output_frame,
            text="Browse",
            command=self.browse_output
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="")
        self.status_label.pack(pady=5)
        
        # Cut button
        self.cut_button = ttk.Button(
            self.main_frame,
            text="Cut Video",
            command=self.cut_video,
            state=tk.DISABLED
        )
        self.cut_button.pack(pady=10)
        
        # Enable drag and drop
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Store current video file path
        self.current_video_path = None
        
        # Check ffmpeg availability
        self.ffmpeg_path = self.check_ffmpeg()
        if not self.ffmpeg_path:
            self.status_label.config(text="Error: ffmpeg not found. Please install ffmpeg and add it to your PATH.")
    
    def check_ffmpeg(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if sys.platform == "win32":
            ffmpeg_path = os.path.join(script_dir, "ffmpeg/bin/ffmpeg.exe")
        else:
            ffmpeg_path = os.path.join(script_dir, "ffmpeg/bin/ffmpeg")
            
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
            
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return "ffmpeg"
        except (subprocess.SubprocessError, FileNotFoundError):
            return None
    
    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.process_video_file(file_path)
    
    def handle_drop(self, event):
        file_path = event.data
        # Remove curly braces if present
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.process_video_file(file_path)
    
    def process_video_file(self, file_path):
        self.current_video_path = file_path
        self.cut_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
        
    
    def browse_output(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, output_dir)
    
    def cut_video(self):
        if not self.current_video_path:
            self.status_label.config(text="Error: No video file selected")
            return
            
        try:
            start_time = float(self.start_time.get())
            end_time = float(self.end_time.get())
            output_dir = self.output_path.get()
            prefix = self.prefix.get().strip()
            
            if not output_dir:
                self.status_label.config(text="Error: Please select output directory")
                return
                
            if not prefix:
                self.status_label.config(text="Error: Please enter a prefix")
                return
                
            if start_time >= end_time:
                self.status_label.config(text="Error: Start time must be less than end time")
                return
                
            # Create output filename
            audio_output = os.path.join(output_dir, f"{prefix}_{start_time}_{end_time}.wav")
            
            # Extract audio
            audio_cmd = [
                self.ffmpeg_path,
                "-i", self.current_video_path,
                "-ss", str(start_time),
                "-to", str(end_time),
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "2",
                "-y",
                audio_output
            ]
            
            # Run command
            self.status_label.config(text="Processing audio...")
            subprocess.run(audio_cmd, check=True)
            
            self.status_label.config(text=f"Success! Audio saved to: {audio_output}")
            
        except ValueError:
            self.status_label.config(text="Error: Please enter valid time values")
        except subprocess.SubprocessError as e:
            self.status_label.config(text=f"Error during processing: {str(e)}")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

def main():
    root = TkinterDnD.Tk()
    app = VideoInfoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
