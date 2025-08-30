#!/usr/bin/env python3
"""
MkDocs hook to automatically generate LLM-friendly files during build.

This hook runs the generate_llm_files.py script during the MkDocs build process
to ensure llms.txt and llms-full.txt are always up to date.
"""

import subprocess
import sys
from pathlib import Path


def on_post_build(config, **kwargs):
    """
    Hook that runs after MkDocs builds the site.
    
    This generates the LLM files and copies them to the site directory
    so they're available in the built documentation.
    """
    try:
        # Run the LLM file generation script
        result = subprocess.run([
            sys.executable, 'generate_llm_files.py'
        ], capture_output=True, text=True, cwd=config['docs_dir'] + '/..')
        
        if result.returncode != 0:
            print(f"Warning: Failed to generate LLM files: {result.stderr}")
            return
        
        print("✓ Generated LLM files successfully")
        
        # Copy the generated files to the site directory
        site_dir = Path(config['site_dir'])
        root_dir = Path(config['docs_dir']).parent
        
        for filename in ['llms.txt', 'llms-full.txt']:
            src_file = root_dir / filename
            dest_file = site_dir / filename
            
            if src_file.exists():
                dest_file.write_text(src_file.read_text(encoding='utf-8'), encoding='utf-8')
                print(f"✓ Copied {filename} to site directory")
        
    except Exception as e:
        print(f"Warning: Error in LLM file generation hook: {e}")
        # Don't fail the build, just warn