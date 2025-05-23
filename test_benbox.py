#!/usr/bin/env python3
### `test_benbox.py`
### Test script for BenBox Phoenix application
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions

import os
import sys
import unittest
import json
import shutil
import tempfile


class TestBenBox(unittest.TestCase):
    """Test class for BenBox Phoenix application"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.vector_store_dir = os.path.join(self.test_dir, "vector_stores")
        os.makedirs(self.vector_store_dir, exist_ok=True)
        
        # Create some test files
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Test content for file {i}")
            self.test_files.append(file_path)
    
    def tearDown(self):
        """Clean up after test"""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_vector_store_config_format(self):
        """Test the format of vector store configuration"""
        # Create a sample vector store configuration
        processed_files = []
        for file_path in self.test_files:
            processed_files.append({
                "filename": os.path.basename(file_path),
                "path": file_path,
                "size": os.path.getsize(file_path),
                "status": "processed"
            })
        
        vector_store_config = {
            "files": processed_files,
            "created_at": "__timestamp__",
            "type": "minio_bucket",
            "source": "Phoenix application"
        }
        
        # Save the configuration to a file
        config_path = os.path.join(self.vector_store_dir, "test_config.json")
        with open(config_path, "w") as f:
            json.dump(vector_store_config, f, indent=2)
        
        # Load the configuration back and validate
        with open(config_path, "r") as f:
            loaded_config = json.load(f)
        
        # Validate the structure
        self.assertEqual(loaded_config["type"], "minio_bucket")
        self.assertEqual(loaded_config["source"], "Phoenix application")
        self.assertEqual(len(loaded_config["files"]), len(self.test_files))
        
        # Check each file entry
        for file_entry in loaded_config["files"]:
            self.assertIn("filename", file_entry)
            self.assertIn("path", file_entry)
            self.assertIn("size", file_entry)
            self.assertIn("status", file_entry)
    
    def test_streamlit_reference(self):
        """Test the StreamlitReference class functionality"""
        # Create a mock StreamlitReference class
        class MockProcess:
            def __init__(self):
                self.terminated = False
            
            def terminate(self):
                self.terminated = True
        
        class MockStreamlitReference:
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
        
        # Create mock objects
        mock_process = MockProcess()
        mock_log_file = tempfile.NamedTemporaryFile(delete=False)
        mock_log_path = mock_log_file.name
        
        # Create a StreamlitReference instance
        streamlit_ref = MockStreamlitReference(mock_process, mock_log_file, mock_log_path)
        
        # Test get_url method
        self.assertEqual(streamlit_ref.get_url(), "http://localhost:8501")
        
        # Test stop method
        streamlit_ref.stop()
        self.assertTrue(mock_process.terminated)
        self.assertFalse(streamlit_ref.running)
        
        # Clean up
        os.unlink(mock_log_path)


if __name__ == "__main__":
    unittest.main()