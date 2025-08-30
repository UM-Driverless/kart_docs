#!/usr/bin/env python3
"""
Generate LLM-friendly files from MkDocs documentation.

This script generates:
- llms.txt: A sitemap-style file with page descriptions
- llms-full.txt: Complete documentation content in one file

Usage:
    python generate_llm_files.py
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


def load_mkdocs_config(config_path: str = "mkdocs.yml") -> Dict:
    """Load MkDocs configuration file."""
    # Custom YAML loader to handle MkDocs-specific tags like !ENV
    class MkDocsLoader(yaml.SafeLoader):
        pass
    
    def env_constructor(loader, node):
        """Handle !ENV tags by ignoring them for our purposes."""
        return None
    
    MkDocsLoader.add_constructor('!ENV', env_constructor)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=MkDocsLoader)


def extract_nav_pages(nav_config: List) -> List[Tuple[str, str, str]]:
    """Extract pages from navigation structure.
    
    Returns:
        List of tuples (title, file_path, url_path)
    """
    pages = []
    base_url = "https://um-driverless.github.io/kart_docs"
    
    def process_nav_item(item, parent_path=""):
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str):
                    # Direct page
                    file_path = f"docs/{value}"
                    url_path = value.replace('.md', '/').replace('index/', '')
                    if url_path.endswith('/'):
                        url_path = url_path[:-1]
                    full_url = f"{base_url}/{url_path}" if url_path else base_url
                    pages.append((key, file_path, full_url))
                elif isinstance(value, list):
                    # Nested section
                    for sub_item in value:
                        process_nav_item(sub_item, key)
        elif isinstance(item, str):
            # Simple string reference
            file_path = f"docs/{item}"
            url_path = item.replace('.md', '/').replace('index/', '')
            if url_path.endswith('/'):
                url_path = url_path[:-1]
            full_url = f"{base_url}/{url_path}" if url_path else base_url
            title = Path(item).stem.replace('-', ' ').title()
            pages.append((title, file_path, full_url))
    
    for item in nav_config:
        process_nav_item(item)
    
    return pages


def read_markdown_file(file_path: str) -> str:
    """Read markdown file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"# File not found: {file_path}"
    except Exception as e:
        return f"# Error reading {file_path}: {str(e)}"


def generate_page_description(title: str, content: str) -> str:
    """Generate a brief description for a page based on its content."""
    lines = content.split('\n')
    
    # Try to find the first paragraph or meaningful content
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('<!--') and not line.startswith('>'):
            # Clean up the description
            description = line.replace('*', '').replace('**', '').strip()
            if len(description) > 100:
                description = description[:97] + "..."
            return description
    
    # Fallback descriptions based on title
    fallback_descriptions = {
        "battery": "Battery system specifications and setup",
        "camera": "Camera configuration and integration", 
        "computer": "Main computer setup and requirements",
        "motor": "Motor control and specifications",
        "steering": "Steering system overview and components",
        "h-bridge": "H-bridge configuration for steering control",
        "sensor": "Steering angle sensor setup and calibration",
        "dac": "Digital-to-analog converter configuration",
        "esp32": "ESP32 microcontroller setup and programming",
        "electrical": "Electrical system wiring and safety",
        "pneumatics": "Pneumatic system components and operation",
        "hydraulics": "Hydraulic system setup and maintenance",
        "assembly": "Step-by-step assembly instructions",
        "software": "Software stack and development setup",
        "faq": "Frequently asked questions and troubleshooting",
        "contact": "Contact information and support channels"
    }
    
    title_lower = title.lower()
    for key, desc in fallback_descriptions.items():
        if key in title_lower:
            return desc
    
    return f"{title} documentation and information"


def generate_llms_txt(pages: List[Tuple[str, str, str]]) -> str:
    """Generate llms.txt content."""
    content = []
    content.append("# Driverless Kart Documentation")
    content.append("")
    content.append("This documentation provides comprehensive information about the autonomous KART project.")
    content.append("")
    
    current_section = None
    
    for title, file_path, url in pages:
        # Read the file to get a description
        markdown_content = read_markdown_file(file_path)
        description = generate_page_description(title, markdown_content)
        
        # Group by sections
        if '/' in file_path and 'hardware/' in file_path:
            if current_section != "Hardware":
                content.append("## Hardware")
                content.append("")
                current_section = "Hardware"
        elif any(section in file_path for section in ['electrical/', 'pneumatics/', 'hydraulics/']):
            if current_section != "Systems":
                content.append("## Systems")
                content.append("")
                current_section = "Systems"
        elif any(section in file_path for section in ['assembly/', 'software/']):
            if current_section != "Assembly & Software":
                content.append("## Assembly & Software")
                content.append("")
                current_section = "Assembly & Software"
        elif any(section in file_path for section in ['faq.md', 'contact.md']):
            if current_section != "Support":
                content.append("## Support")
                content.append("")
                current_section = "Support"
        elif current_section != "Overview" and title != "KART Documentation":
            if current_section != "Overview":
                content.append("## Overview")
                content.append("")
                current_section = "Overview"
        
        content.append(f"{url}")
        content.append(description)
        content.append("")
    
    return '\n'.join(content)


def generate_llms_full_txt(pages: List[Tuple[str, str, str]]) -> str:
    """Generate llms-full.txt content."""
    content = []
    content.append("# Driverless Kart Documentation - Complete Content")
    content.append("")
    content.append("This document contains the complete documentation for the autonomous KART project by Ü Motorsport Formula Student team.")
    content.append("")
    content.append("---")
    content.append("")
    
    for title, file_path, url in pages:
        markdown_content = read_markdown_file(file_path)
        
        # Add section header
        section_title = title
        if title == "KART Documentation":
            section_title = "Home - KART Documentation"
        elif "hardware/" in file_path:
            section_title = f"Hardware - {title}"
        elif file_path == "docs/electrical/index.md":
            section_title = "Electrical - Wiring"
        elif file_path == "docs/assembly/index.md":
            section_title = "Assembly Instructions"
        elif file_path == "docs/software/index.md":
            section_title = "Software"
        elif file_path == "docs/faq.md":
            section_title = "Frequently Asked Questions"
        elif file_path == "docs/contact.md":
            section_title = "Contact"
        
        content.append(f"## {section_title}")
        content.append("")
        
        # Clean up the content
        cleaned_content = markdown_content
        
        # Remove TODO comments at the start
        lines = cleaned_content.split('\n')
        cleaned_lines = []
        skip_todo_block = False
        
        for line in lines:
            if line.strip().startswith('<!-- TODO'):
                skip_todo_block = True
            elif skip_todo_block and line.strip().endswith('-->'):
                skip_todo_block = False
                continue
            elif not skip_todo_block:
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines).strip()
        
        # Remove the first # header if it exists (we add our own)
        if cleaned_content.startswith('# '):
            first_newline = cleaned_content.find('\n')
            if first_newline != -1:
                cleaned_content = cleaned_content[first_newline+1:].strip()
        
        content.append(cleaned_content)
        content.append("")
        content.append("---")
        content.append("")
    
    # Add footer
    content.append("*This documentation is available at https://um-driverless.github.io/kart_docs/ and follows the llms.txt standard for LLM consumption.*")
    
    return '\n'.join(content)


def main():
    """Main function to generate LLM files."""
    try:
        # Load MkDocs configuration
        config = load_mkdocs_config()
        
        # Extract pages from navigation
        pages = extract_nav_pages(config.get('nav', []))
        
        print(f"Found {len(pages)} pages in documentation")
        
        # Generate llms.txt
        llms_content = generate_llms_txt(pages)
        with open('llms.txt', 'w', encoding='utf-8') as f:
            f.write(llms_content)
        print("✓ Generated llms.txt")
        
        # Generate llms-full.txt
        llms_full_content = generate_llms_full_txt(pages)
        with open('llms-full.txt', 'w', encoding='utf-8') as f:
            f.write(llms_full_content)
        print("✓ Generated llms-full.txt")
        
        print("\nLLM-friendly files generated successfully!")
        print("- llms.txt: Sitemap-style overview")
        print("- llms-full.txt: Complete documentation content")
        
    except Exception as e:
        print(f"Error generating LLM files: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())