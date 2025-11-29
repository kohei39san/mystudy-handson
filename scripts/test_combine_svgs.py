#!/usr/bin/env python3
"""
Test script for the SVG combiner functionality.
Creates simple test SVG files and tests the combination.
"""

import os
import tempfile
import sys
from combine_svgs import combine_svgs

def create_test_svg(filename, width, height, color, text):
    """Create a simple test SVG file."""
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect x="10" y="10" width="{width-20}" height="{height-20}" fill="{color}" stroke="black" stroke-width="2"/>
    <text x="{width//2}" y="{height//2}" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="16">{text}</text>
</svg>'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)

def test_svg_combination():
    """Test the SVG combination functionality."""
    print("Testing SVG combination...")
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test SVG files
        svg1 = os.path.join(temp_dir, "test1.svg")
        svg2 = os.path.join(temp_dir, "test2.svg")
        svg3 = os.path.join(temp_dir, "test3.svg")
        output = os.path.join(temp_dir, "combined.svg")
        
        create_test_svg(svg1, 200, 100, "#ff6b6b", "Page 1")
        create_test_svg(svg2, 250, 120, "#4ecdc4", "Page 2")
        create_test_svg(svg3, 180, 80, "#45b7d1", "Page 3")
        
        print(f"Created test files: {svg1}, {svg2}, {svg3}")
        
        # Test combination
        success = combine_svgs(output, [svg1, svg2, svg3], spacing=10)
        
        if success and os.path.exists(output):
            print(f"✅ Test passed! Combined SVG created at: {output}")
            
            # Read and display some info about the result
            with open(output, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Combined SVG size: {len(content)} characters")
                if 'Page 1' in content and 'Page 2' in content and 'Page 3' in content:
                    print("✅ All pages found in combined SVG")
                else:
                    print("❌ Not all pages found in combined SVG")
            
            return True
        else:
            print("❌ Test failed! Could not create combined SVG")
            return False

if __name__ == "__main__":
    success = test_svg_combination()
    sys.exit(0 if success else 1)