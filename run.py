#!/usr/bin/env python3
"""Run script for VWatch application"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Run the streamlit app
if __name__ == "__main__":
    os.system(f"streamlit run {Path(__file__).parent}/app/ui.py")