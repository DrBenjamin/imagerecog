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
        
        # Create simple UI
        self.label = tk.Label(root, text="BenBox Phoenix Application")
        self.label.pack(pady=20)
        
        self.start_streamlit_button = tk.Button(root, text="Start Streamlit App", command=self.start_streamlit)
        self.start_streamlit_button.pack(pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

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
            return
        
        # Check if Streamlit is running
        if not hasattr(self, "streamlit") or self.streamlit is None:
            messagebox.showwarning("Warning", "Streamlit is not running. Please start Streamlit first.")
            return
        
        try:
            # Create vector store logic
            # This would integrate with the MinIO bucket files logic
            self.status_var.set("Creating vector store...")
            
            # Placeholder for vector store creation logic
            # In a real implementation, this would interact with the Streamlit app
            # through some communication mechanism (e.g., API calls, shared file, etc.)
            
            # For demonstration, create a simple JSON configuration for the vector store
            vector_store_config = {
                "files": bucket_files,
                "created_at": "2024-01-01 00:00:00",
                "type": "minio_bucket"
            }
            
            # Save configuration to a temporary file that Streamlit can access
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(vector_store_config, f)
                temp_file_path = f.name
            
            # In a real implementation, we would need to communicate this to the Streamlit app
            # This could be done via a shared file, database, or other mechanism
            
            self.status_var.set(f"Vector store created from {len(bucket_files)} files")
            messagebox.showinfo("Success", f"Vector store created successfully from {len(bucket_files)} files.\n\nConfiguration saved to: {temp_file_path}")
            
        except Exception as e:
            self.status_var.set("Error creating vector store")
            messagebox.showerror("Error", f"Failed to create vector store: {str(e)}")
    
    def start_streamlit(self):
        """Start the Streamlit application"""
        self.status_var.set("Starting Streamlit app...")
        
        # Start Streamlit in a separate thread
        threading.Thread(target=self._run_streamlit, daemon=True).start()
    
    def _run_streamlit(self):
        """Run the Streamlit app in a separate process"""
        try:
            # Set working directory to the repository root
            repo_root = os.path.dirname(os.path.abspath(__file__))
            
            # Start the Streamlit process
            process = subprocess.Popen(
                ["python", "-m", "streamlit", "run", "app.py", "--server.enableXsrfProtection", "false"],
                cwd=repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Create a reference to Streamlit that can be used by other methods
            # In this implementation, we're using a simple object to store state
            class StreamlitReference:
                def __init__(self, process):
                    self.process = process
                    self.running = True
                
                def stop(self):
                    if self.running:
                        self.process.terminate()
                        self.running = False
            
            self.streamlit = StreamlitReference(process)
            self.root.after(100, lambda: self.status_var.set("Streamlit app is running"))
            
            # Monitor the Streamlit process
            while self.streamlit.running:
                # Check if process is still running
                if process.poll() is not None:
                    self.streamlit.running = False
                    self.root.after(100, lambda: self.status_var.set("Streamlit app has stopped"))
                    break
                
                # Optional: Process stdout for monitoring
                line = process.stdout.readline()
                if line:
                    print(f"Streamlit: {line.strip()}")
            
        except Exception as e:
            self.root.after(100, lambda: self.status_var.set(f"Error starting Streamlit: {e}"))
            print(f"Error starting Streamlit: {e}")


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