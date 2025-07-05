#!/usr/bin/env python3
"""
Script to update markdown files in the repository based on the content of their directories.
This script:
1. Finds all markdown files in the repository
2. For each markdown file, analyzes the content of the directory it's in
3. Updates the markdown file to ensure its description is accurate and up-to-date
"""

import os
import re
import glob
import subprocess
from pathlib import Path

def get_file_content(file_path):
    """Read and return the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_file_content(file_path, content):
    """Write content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def get_directory_structure(directory):
    """Get the structure of files and directories in the given directory."""
    result = []
    
    try:
        # List all files and directories in the given directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Skip hidden files and directories
            if item.startswith('.'):
                continue
                
            if os.path.isdir(item_path):
                result.append(f"Directory: {item}")
            else:
                result.append(f"File: {item}")
    except Exception as e:
        print(f"Error getting directory structure for {directory}: {e}")
    
    return result

def get_file_descriptions(directory):
    """Get descriptions of files in the directory based on their content."""
    descriptions = {}
    
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Skip hidden files and directories
            if item.startswith('.'):
                continue
                
            if os.path.isfile(item_path):
                # Get file extension
                _, ext = os.path.splitext(item)
                
                # Handle different file types
                if ext.lower() in ['.tf', '.tfvars']:
                    # For Terraform files, try to determine their purpose
                    content = get_file_content(item_path)
                    if content:
                        if 'provider "aws"' in content or 'terraform {' in content:
                            descriptions[item] = "Terraform configuration file"
                        elif 'variable "' in content:
                            descriptions[item] = "Terraform variables definition file"
                        elif 'output "' in content:
                            descriptions[item] = "Terraform outputs definition file"
                        elif 'resource "' in content:
                            descriptions[item] = "Terraform resource definition file"
                        elif 'module "' in content:
                            descriptions[item] = "Terraform module configuration file"
                        else:
                            descriptions[item] = "Terraform file"
                elif ext.lower() == '.py':
                    descriptions[item] = "Python script"
                elif ext.lower() == '.sh':
                    descriptions[item] = "Shell script"
                elif ext.lower() == '.ps1':
                    descriptions[item] = "PowerShell script"
                elif ext.lower() == '.yaml' or ext.lower() == '.yml':
                    # For YAML files, check if it's CloudFormation
                    content = get_file_content(item_path)
                    if content and ('AWSTemplateFormatVersion' in content or 'Resources:' in content):
                        descriptions[item] = "AWS CloudFormation template"
                    else:
                        descriptions[item] = "YAML configuration file"
                elif ext.lower() == '.json':
                    descriptions[item] = "JSON configuration file"
                else:
                    descriptions[item] = f"{ext[1:].upper()} file"
    except Exception as e:
        print(f"Error getting file descriptions for {directory}: {e}")
    
    return descriptions

def update_markdown_file(md_file):
    """Update a markdown file based on the content of its directory."""
    print(f"Processing {md_file}...")
    
    # Get the directory containing the markdown file
    directory = os.path.dirname(md_file)
    
    # Read the current content of the markdown file
    content = get_file_content(md_file)
    if not content:
        return False
    
    # Get information about the directory structure
    dir_structure = get_directory_structure(directory)
    file_descriptions = get_file_descriptions(directory)
    
    # Check if the markdown file is a README.md
    is_readme = os.path.basename(md_file).lower() == 'readme.md'
    
    # Create updated content based on the directory structure
    updated_content = content
    
    # If it's a README.md, update the file list section if it exists
    if is_readme:
        # Look for a section that lists files or directory structure
        file_section_patterns = [
            r'(## ファイル構成\s*\n)(.*?)(\n##|\Z)',
            r'(## ファイル\s*\n)(.*?)(\n##|\Z)',
            r'(## Files\s*\n)(.*?)(\n##|\Z)',
            r'(## File Structure\s*\n)(.*?)(\n##|\Z)',
            r'(## Directory Structure\s*\n)(.*?)(\n##|\Z)',
            r'(## Structure\s*\n)(.*?)(\n##|\Z)',
            r'(## コンポーネント\s*\n)(.*?)(\n##|\Z)'
        ]
        
        section_found = False
        for pattern in file_section_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section_found = True
                section_header = match.group(1)
                section_content = ""
                
                # Generate new content for the section
                if file_descriptions:
                    section_content += "このディレクトリには以下のファイルが含まれています：\n\n"
                    for file_name, description in file_descriptions.items():
                        section_content += f"- **{file_name}**: {description}\n"
                
                # Update the section in the content
                updated_content = content.replace(match.group(0), f"{section_header}{section_content}\n\n##" if match.group(3) == "\n##" else f"{section_header}{section_content}")
                break
        
        # If no file section was found but we have files to describe, add a new section
        if not section_found and file_descriptions:
            # Find a good place to insert the new section
            # Try to insert after the introduction or overview section
            intro_patterns = [
                r'(## 概要\s*\n.*?)(\n##|\Z)',
                r'(## Overview\s*\n.*?)(\n##|\Z)',
                r'(## Introduction\s*\n.*?)(\n##|\Z)'
            ]
            
            insert_position = None
            for pattern in intro_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    insert_position = match.end(1)
                    break
            
            if insert_position:
                # Create the new section
                new_section = "\n\n## ファイル構成\n\nこのディレクトリには以下のファイルが含まれています：\n\n"
                for file_name, description in file_descriptions.items():
                    new_section += f"- **{file_name}**: {description}\n"
                
                # Insert the new section
                updated_content = content[:insert_position] + new_section + content[insert_position:]
    
    # Check if the content has been updated
    if updated_content != content:
        return write_file_content(md_file, updated_content)
    else:
        print(f"No updates needed for {md_file}")
        return True

def find_markdown_files(base_dir):
    """Find all markdown files in the repository."""
    md_files = []
    
    # Use glob to find all .md files
    for md_file in glob.glob(f"{base_dir}/**/*.md", recursive=True):
        # Skip files in hidden directories
        if not any(part.startswith('.') for part in Path(md_file).parts):
            md_files.append(md_file)
    
    return md_files

def main():
    """Main function to update all markdown files in the repository."""
    # Base directory is the current working directory
    base_dir = os.getcwd()
    
    print(f"Searching for markdown files in {base_dir}...")
    md_files = find_markdown_files(base_dir)
    print(f"Found {len(md_files)} markdown files.")
    
    # Update each markdown file
    for md_file in md_files:
        update_markdown_file(md_file)

if __name__ == "__main__":
    main()