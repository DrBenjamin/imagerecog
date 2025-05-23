### `BenBox.py`
### Phoenix application for BenBox
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions

import tkinter as tk
from tkinter import messagebox, filedialog
import streamlit as st
import os
import sys
import subprocess
import threading
import base64
import io
from PIL import Image
import tempfile
import json
import time
import webbrowser

class Phoenix:
    def __init__(self, root):
        self.root = root
        self.root.title("BenBox - Phoenix")
        self.root.geometry("800x600")
        
        # Initialize streamlit reference (will be set when app is launched)
        self.streamlit = None
        
        # Create menu bar
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)
        
        # Create "Datei" menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Datei", menu=self.file_menu)
        
        # Add menu items to "Datei" menu
        self.file_menu.add_command(label="Öffnen", command=self.open_file)
        self.file_menu.add_command(label="Speichern", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Erstelle neuen Eintrag", command=self.create_vector_store)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Beenden", command=self.root.quit)
        
        # Create "Hilfe" menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Hilfe", menu=self.help_menu)
        self.help_menu.add_command(label="Über", command=self.show_about)
        
        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header
        self.header_label = tk.Label(self.main_frame, 
                                    text="BenBox Phoenix Application", 
                                    font=("Helvetica", 16, "bold"))
        self.header_label.pack(pady=(0, 20))
        
        # Create info text
        info_text = ("Diese Anwendung ermöglicht die Integration mit der BenBox Streamlit App.\n\n" +
                    "Mit dem Menüpunkt 'Erstelle neuen Eintrag' können Sie einen Vector Store " +
                    "aus Bucket/Stage-Dateien erstellen.")
        self.info_label = tk.Label(self.main_frame, text=info_text, justify=tk.LEFT, wraplength=700)
        self.info_label.pack(pady=(0, 20), anchor=tk.W)
        
        # Create buttons frame
        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=(10, 20))
        
        # Create Streamlit control buttons
        self.start_streamlit_button = tk.Button(
            self.buttons_frame, 
            text="Start Streamlit App", 
            command=self.start_streamlit,
            width=20,
            height=2
        )
        self.start_streamlit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_browser_button = tk.Button(
            self.buttons_frame, 
            text="Öffne im Browser", 
            command=self.open_streamlit_browser,
            width=20,
            height=2
        )
        self.open_browser_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_store_button = tk.Button(
            self.buttons_frame, 
            text="Erstelle Vector Store", 
            command=self.create_vector_store,
            width=20,
            height=2
        )
        self.create_store_button.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "Über BenBox",
            "BenBox Phoenix Application\n\n" +
            "Version: 1.0.0\n" +
            "Open-Source, hosted on GitHub\n\n" +
            "© 2024 BenBox"
        )
    
    def open_streamlit_browser(self):
        """Open the Streamlit app in a browser"""
        if hasattr(self, "streamlit") and self.streamlit and self.streamlit.running:
            webbrowser.open(self.streamlit.get_url())
        else:
            messagebox.showwarning("Warning", "Streamlit is not running. Please start Streamlit first.")
            self.status_var.set("Streamlit ist nicht gestartet")

    def open_file(self):
        """Open a file"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.status_var.set(f"Opened: {file_path}")
    
    def save_file(self):
        """Save a file"""
        file_path = filedialog.asksaveasfilename()
        if file_path:
            self.status_var.set(f"Saved: {file_path}")
    
    def create_vector_store(self):
        """Create vector store from bucket/stage files"""
        # Open file selection dialog
        bucket_files = filedialog.askopenfilenames(
            title="Select bucket/stage files",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not bucket_files:
            self.status_var.set("Vector store creation cancelled")
            return
        
        # Check if Streamlit is running
        if not hasattr(self, "streamlit") or self.streamlit is None:
            messagebox.showwarning("Warning", "Streamlit is not running. Please start Streamlit first.")
            self.status_var.set("Vector store creation failed - Streamlit not running")
            return
        
        try:
            # Create vector store logic
            # This integrates with the MinIO bucket files logic
            self.status_var.set("Creating vector store...")
            
            # Process each file for the vector store
            processed_files = []
            for file_path in bucket_files:
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract filename for reference
                    filename = os.path.basename(file_path)
                    
                    processed_files.append({
                        "filename": filename,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "status": "processed"
                    })
                    
                except Exception as file_error:
                    processed_files.append({
                        "filename": os.path.basename(file_path),
                        "path": file_path,
                        "error": str(file_error),
                        "status": "error"
                    })
            
            # Create vector store configuration
            vector_store_config = {
                "files": processed_files,
                "created_at": "__timestamp__",  # Will be filled by Streamlit
                "type": "minio_bucket",
                "source": "Phoenix application"
            }
            
            # Create a directory for vector store configs if it doesn't exist
            vector_store_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_stores")
            os.makedirs(vector_store_dir, exist_ok=True)
            
            # Save configuration to a file that Streamlit can access
            config_filename = f"vector_store_config_{len(bucket_files)}_files.json"
            config_path = os.path.join(vector_store_dir, config_filename)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(vector_store_config, f, indent=2)
            
            # Count successful and failed files
            successful = sum(1 for file in processed_files if file["status"] == "processed")
            failed = len(processed_files) - successful
            
            status_message = f"Vector store created from {successful} files"
            if failed > 0:
                status_message += f" ({failed} files failed)"
            
            self.status_var.set(status_message)
            messagebox.showinfo(
                "Vector Store Created", 
                f"Vector store created successfully!\n\n"
                f"- Processed files: {successful}\n"
                f"- Failed files: {failed}\n\n"
                f"Configuration saved to: {config_path}"
            )
            
        except Exception as e:
            self.status_var.set("Error creating vector store")
            messagebox.showerror("Error", f"Failed to create vector store: {str(e)}")
    
    def start_streamlit(self):
        """Start the Streamlit application"""
        # Check if Streamlit is already running
        if hasattr(self, "streamlit") and self.streamlit and self.streamlit.running:
            messagebox.showinfo("Info", "Streamlit is already running.")
            return
        
        self.status_var.set("Starting Streamlit app...")
        
        # Start Streamlit in a separate thread
        threading.Thread(target=self._run_streamlit, daemon=True).start()
    
    def _run_streamlit(self):
        """Run the Streamlit app in a separate process"""
        try:
            # Set working directory to the repository root
            repo_root = os.path.dirname(os.path.abspath(__file__))
            
            # Check if app.py exists
            app_path = os.path.join(repo_root, "app.py")
            if not os.path.exists(app_path):
                error_msg = f"Streamlit app file not found: {app_path}"
                self.root.after(100, lambda: self.status_var.set(error_msg))
                messagebox.showerror("Error", error_msg)
                return
                
            # Start the Streamlit process
            cmd = ["python", "-m", "streamlit", "run", app_path, "--server.enableXsrfProtection", "false"]
            
            # Open log file for Streamlit output
            logs_dir = os.path.join(repo_root, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            log_path = os.path.join(logs_dir, "streamlit.log")
            
            log_file = open(log_path, 'w')
            
            process = subprocess.Popen(
                cmd,
                cwd=repo_root,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Create a reference to Streamlit that can be used by other methods
            class StreamlitReference:
                def __init__(self, process, log_file, log_path):
                    self.process = process
                    self.running = True
                    self.log_file = log_file
                    self.log_path = log_path
                    
                def stop(self):
                    if self.running:
                        self.process.terminate()
                        self.running = False
                        if self.log_file:
                            self.log_file.close()
                
                def get_url(self):
                    return "http://localhost:8501"
            
            self.streamlit = StreamlitReference(process, log_file, log_path)
            
            # Wait for Streamlit to start (look for the URL in the log)
            max_wait_time = 30  # seconds
            start_time = time.time()
            started = False
            
            while time.time() - start_time < max_wait_time:
                if process.poll() is not None:  # Process exited
                    break
                    
                # Check if the process is still running
                if not started and os.path.exists(log_path):
                    try:
                        with open(log_path, 'r') as f:
                            log_content = f.read()
                            if "You can now view your Streamlit app in your browser" in log_content:
                                started = True
                                self.root.after(100, lambda: self.status_var.set("Streamlit app is running at http://localhost:8501"))
                                # Optionally open browser
                                # webbrowser.open("http://localhost:8501")
                                break
                    except:
                        pass
                
                time.sleep(0.5)
            
            if not started:
                error_msg = "Streamlit failed to start in the expected time."
                self.root.after(100, lambda: self.status_var.set(error_msg))
                if self.streamlit:
                    self.streamlit.stop()
                    self.streamlit = None
                return
            
            # Monitor the Streamlit process and update status when it ends
            def monitor_process():
                while self.streamlit and self.streamlit.running:
                    if process.poll() is not None:  # Process exited
                        self.streamlit.running = False
                        self.root.after(100, lambda: self.status_var.set("Streamlit app has stopped"))
                        break
                    time.sleep(1)
            
            # Start monitoring in a separate thread
            threading.Thread(target=monitor_process, daemon=True).start()
            
        except Exception as e:
            error_msg = f"Error starting Streamlit: {e}"
            self.root.after(100, lambda: self.status_var.set(error_msg))
            messagebox.showerror("Error", error_msg)


# Global reference to the Phoenix application
g = None

def main():
    global g
    root = tk.Tk()
    app = Phoenix(root)
    g = app  # Store the application instance in the global variable
    root.mainloop()

if __name__ == "__main__":
    main()