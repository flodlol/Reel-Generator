#!/usr/bin/env python3
"""
Meme Video Generator - Application Launcher

Run this file to launch the GUI application.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.app import main

if __name__ == "__main__":
    main()
