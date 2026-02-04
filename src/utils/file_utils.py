"""
File and path utilities.

This module provides helper functions for file operations and path manipulation.
"""

import os
import re
from pathlib import Path
from typing import List, Optional


def shorten_path(path: str, base_folder: str = 'Project-Memes') -> str:
    """
    Shorten a file path by keeping only the path relative to the base folder.
    
    Args:
        path: Full file path
        base_folder: Base folder name to shorten from
        
    Returns:
        Shortened path string
    """
    base_index = path.find(base_folder)
    if base_index != -1:
        return path[base_index:]
    return path


def ensure_dir(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to create
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_next_filename(
    folder: str,
    prefix: str,
    extension: str,
    start_from: int = 1
) -> int:
    """
    Find the next available filename number in a folder.
    
    Args:
        folder: Folder to search
        prefix: Filename prefix (e.g., 'meme_')
        extension: File extension (e.g., '.mp4')
        start_from: Starting number to search from
        
    Returns:
        Next available number
    """
    if not os.path.exists(folder):
        return start_from
    
    files = os.listdir(folder)
    matching_files = [f for f in files if f.startswith(prefix) and f.endswith(extension)]
    
    if not matching_files:
        return start_from
    
    numbers = []
    for filename in matching_files:
        match = re.search(r'\d+', filename)
        if match:
            numbers.append(int(match.group()))
    
    return max(numbers) + 1 if numbers else start_from


def get_latest_filename(
    folder: str,
    prefix: str,
    extension: str
) -> Optional[str]:
    """
    Get the latest filename with the highest number in a folder.
    
    Args:
        folder: Folder to search
        prefix: Filename prefix
        extension: File extension
        
    Returns:
        Latest filename or None if no matching files found
    """
    if not os.path.exists(folder):
        return None
    
    files = os.listdir(folder)
    matching_files = [f for f in files if f.startswith(prefix) and f.endswith(extension)]
    
    if not matching_files:
        return None
    
    # Sort by number in filename
    def get_number(filename):
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else 0
    
    return max(matching_files, key=get_number)


def list_files(
    folder: str,
    extensions: Optional[List[str]] = None,
    pattern: Optional[str] = None
) -> List[str]:
    """
    List files in a folder with optional filtering.
    
    Args:
        folder: Folder to search
        extensions: List of extensions to filter by (e.g., ['.jpg', '.png'])
        pattern: Regex pattern to match filenames
        
    Returns:
        List of matching filenames
    """
    if not os.path.exists(folder):
        return []
    
    files = os.listdir(folder)
    
    # Filter by extension
    if extensions:
        extensions = [ext.lower() for ext in extensions]
        files = [f for f in files if any(f.lower().endswith(ext) for ext in extensions)]
    
    # Filter by pattern
    if pattern:
        regex = re.compile(pattern)
        files = [f for f in files if regex.search(f)]
    
    return sorted(files)


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    if not os.path.exists(file_path):
        return 0.0
    
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def clean_filename(filename: str) -> str:
    """
    Clean a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename
