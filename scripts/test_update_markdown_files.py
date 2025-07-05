#!/usr/bin/env python3
"""
Unit tests for the update_markdown_files.py script.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Import the functions from the script
from update_markdown_files import (
    get_file_content,
    write_file_content,
    get_directory_structure,
    get_file_descriptions,
    update_markdown_file,
    find_markdown_files
)

class TestUpdateMarkdownFiles(unittest.TestCase):
    """Test cases for the update_markdown_files.py script."""
    
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test directory structure
        self.test_project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.test_project_dir)
        
        # Create a README.md file
        self.readme_path = os.path.join(self.test_project_dir, "README.md")
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write("# Test Project\n\n## 概要\n\nThis is a test project.\n\n## 使い方\n\nHow to use this project.\n")
        
        # Create some test files
        self.tf_file_path = os.path.join(self.test_project_dir, "main.tf")
        with open(self.tf_file_path, "w", encoding="utf-8") as f:
            f.write('provider "aws" {\n  region = "us-west-2"\n}\n')
        
        self.py_file_path = os.path.join(self.test_project_dir, "script.py")
        with open(self.py_file_path, "w", encoding="utf-8") as f:
            f.write('print("Hello, World!")\n')
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_file_content(self):
        """Test the get_file_content function."""
        content = get_file_content(self.readme_path)
        self.assertIsNotNone(content)
        self.assertIn("# Test Project", content)
        
        # Test with a non-existent file
        content = get_file_content(os.path.join(self.temp_dir, "non_existent.md"))
        self.assertIsNone(content)
    
    def test_write_file_content(self):
        """Test the write_file_content function."""
        test_file_path = os.path.join(self.temp_dir, "test_write.txt")
        result = write_file_content(test_file_path, "Test content")
        self.assertTrue(result)
        
        # Verify the content was written
        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "Test content")
        
        # Test writing to a directory (should fail)
        result = write_file_content(self.temp_dir, "Test content")
        self.assertFalse(result)
    
    def test_get_directory_structure(self):
        """Test the get_directory_structure function."""
        structure = get_directory_structure(self.test_project_dir)
        self.assertIsInstance(structure, list)
        self.assertEqual(len(structure), 3)  # README.md, main.tf, script.py
        
        # Check that all files are included
        file_names = [item.split(": ")[1] for item in structure]
        self.assertIn("README.md", file_names)
        self.assertIn("main.tf", file_names)
        self.assertIn("script.py", file_names)
    
    def test_get_file_descriptions(self):
        """Test the get_file_descriptions function."""
        descriptions = get_file_descriptions(self.test_project_dir)
        self.assertIsInstance(descriptions, dict)
        self.assertEqual(len(descriptions), 3)  # README.md, main.tf, script.py
        
        # Check the descriptions
        self.assertIn("main.tf", descriptions)
        self.assertIn("script.py", descriptions)
        self.assertIn("README.md", descriptions)
        self.assertEqual(descriptions["script.py"], "Python script")
    
    def test_update_markdown_file(self):
        """Test the update_markdown_file function."""
        # First run should update the README.md
        result = update_markdown_file(self.readme_path)
        self.assertTrue(result)
        
        # Check that the content was updated
        updated_content = get_file_content(self.readme_path)
        self.assertIn("## ファイル構成", updated_content)
        self.assertIn("main.tf", updated_content)
        self.assertIn("script.py", updated_content)
    
    def test_find_markdown_files(self):
        """Test the find_markdown_files function."""
        # Create a nested directory with a markdown file
        nested_dir = os.path.join(self.test_project_dir, "nested")
        os.makedirs(nested_dir)
        nested_md_path = os.path.join(nested_dir, "nested.md")
        with open(nested_md_path, "w", encoding="utf-8") as f:
            f.write("# Nested Markdown\n")
        
        # Find all markdown files
        md_files = find_markdown_files(self.test_project_dir)
        self.assertEqual(len(md_files), 2)  # README.md and nested.md
        
        # Check that both files are found
        file_names = [os.path.basename(path) for path in md_files]
        self.assertIn("README.md", file_names)
        self.assertIn("nested.md", file_names)

if __name__ == "__main__":
    unittest.main()